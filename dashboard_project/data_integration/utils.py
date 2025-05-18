import csv
import logging
from datetime import datetime

import bleach
import requests
from bleach.css_sanitizer import CSSSanitizer
from django.utils.timezone import make_aware

from .models import ChatMessage, ChatSession, ExternalDataSource

logger = logging.getLogger(__name__)

EXPECTED_HEADERS = [
    "session_id",
    "start_time",
    "end_time",
    "ip_address",
    "country",
    "language",
    "messages_sent",
    "sentiment",
    "escalated",
    "forwarded_hr",
    "full_transcript",
    "avg_response_time",
    "tokens",
    "tokens_eur",
    "category",
    "initial_msg",
    "user_rating",
]


def fetch_and_store_chat_data(source_id=None):
    """Fetch chat data from an external API and store it in the database.

    Args:
        source_id: Optional ID of specific ExternalDataSource to use.
                  If None, will use the first active source.

    Returns:
        dict: Stats about the operation (sessions created, updated, errors)
    """
    if source_id:
        source = ExternalDataSource.objects.filter(id=source_id, is_active=True).first()
        if not source:
            logger.error(f"Data source with ID {source_id} not found or not active.")
            return {
                "success": False,
                "error": f"Data source with ID {source_id} not found or not active.",
            }
    else:
        source = ExternalDataSource.objects.filter(is_active=True).first()
        if not source:
            logger.warning("No active data source found.")
            return {"success": False, "error": "No active data source found."}

    stats = {
        "sessions_created": 0,
        "sessions_updated": 0,
        "transcripts_processed": 0,
        "errors": 0,
        "success": True,
    }

    try:
        # Fetch data from API with timeout from source settings or default
        timeout = getattr(source, "timeout", 30)
        response = requests.get(
            source.api_url,
            auth=((source.get_auth_username(), source.get_auth_password()) if source.get_auth_username() else None),
            timeout=timeout,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        error_msg = f"Error fetching data from API {source.api_url}: {e}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

    # Process CSV data
    csv_data = response.content.decode("utf-8").splitlines()
    reader = csv.reader(csv_data)
    # Skip header if present, or use predefined if not
    # header = next(reader) # Assuming the first row is a header
    # For this specific case, we know the header is missing.
    header = EXPECTED_HEADERS

    for row in reader:
        if not row:  # Skip empty rows
            continue
        try:
            # Fix for zip() argument mismatch: pad the row with empty strings if needed
            padded_row = row + [""] * (len(header) - len(row))
            data = dict(zip(header, padded_row, strict=False))

            try:
                # Try European date format (DD.MM.YYYY) first
                start_time = make_aware(datetime.strptime(data["start_time"], "%d.%m.%Y %H:%M:%S"))
            except ValueError:
                # Fallback to ISO format (YYYY-MM-DD)
                start_time = make_aware(datetime.strptime(data["start_time"], "%Y-%m-%d %H:%M:%S"))

            try:
                # Try European date format (DD.MM.YYYY) first
                end_time = make_aware(datetime.strptime(data["end_time"], "%d.%m.%Y %H:%M:%S"))
            except ValueError:
                # Fallback to ISO format (YYYY-MM-DD)
                end_time = make_aware(datetime.strptime(data["end_time"], "%Y-%m-%d %H:%M:%S"))

            messages_sent = int(data["messages_sent"]) if data["messages_sent"] else None
            escalated = data["escalated"].lower() == "true" if data["escalated"] else None
            forwarded_hr = data["forwarded_hr"].lower() == "true" if data["forwarded_hr"] else None
            avg_response_time = float(data["avg_response_time"]) if data["avg_response_time"] else None
            tokens = int(data["tokens"]) if data["tokens"] else None
            tokens_eur = float(data["tokens_eur"]) if data["tokens_eur"] else None
            user_rating = int(data["user_rating"]) if data["user_rating"] and data["user_rating"].isdigit() else None

            session, created = ChatSession.objects.update_or_create(
                session_id=data["session_id"],
                defaults={
                    "start_time": start_time,
                    "end_time": end_time,
                    "ip_address": data.get("ip_address"),
                    "country": data.get("country"),
                    "language": data.get("language"),
                    "messages_sent": messages_sent,
                    "sentiment": data.get("sentiment"),
                    "escalated": escalated,
                    "forwarded_hr": forwarded_hr,
                    "full_transcript_url": data.get("full_transcript"),
                    "avg_response_time": avg_response_time,
                    "tokens": tokens,
                    "tokens_eur": tokens_eur,
                    "category": data.get("category"),
                    "initial_msg": data.get("initial_msg"),
                    "user_rating": user_rating,
                },
            )

            if created:
                stats["sessions_created"] += 1
                logger.info(f"Created session: {session.session_id}")
            else:
                stats["sessions_updated"] += 1
                logger.info(f"Updated session: {session.session_id}")

            # Fetch and process transcript if URL is present
            if session.full_transcript_url:
                transcript_result = fetch_and_store_transcript(session, timeout)
                if transcript_result["success"]:
                    stats["transcripts_processed"] += 1

        except Exception as e:
            logger.error(f"Error processing row: {row}. Error: {e}", exc_info=True)
            stats["errors"] += 1
            continue

    source.last_synced = make_aware(datetime.now())
    source.save()
    logger.info("Data sync complete. Stats: {stats}")

    return stats


def fetch_and_store_transcript(session, timeout=30):
    """Fetch and process transcript for a chat session.

    Args:
        session: The ChatSession object
        timeout: Timeout in seconds for the request

    Returns:
        dict: Result of the operation
    """
    result = {"success": False, "messages_created": 0, "error": None}

    try:
        transcript_response = requests.get(session.full_transcript_url, timeout=timeout)
        transcript_response.raise_for_status()
        transcript_content = transcript_response.content.decode("utf-8")
        messages_created = parse_and_store_transcript_messages(session, transcript_content)

        result["success"] = True
        result["messages_created"] = messages_created
        return result
    except requests.RequestException as e:
        error_msg = f"Error fetching transcript for session {session.session_id}: {e}"
        logger.error(error_msg)
        result["error"] = error_msg
        return result
    except Exception as e:
        error_msg = f"Error processing transcript for session {session.session_id}: {e}"
        logger.error(error_msg, exc_info=True)
        result["error"] = error_msg
        return result


def parse_and_store_transcript_messages(session, transcript_content):
    """Parse and store messages from a transcript.

    Args:
        session: The ChatSession object
        transcript_content: The raw transcript content

    Returns:
        int: Number of messages created
    """
    lines = transcript_content.splitlines()
    current_sender = None
    current_message_lines = []
    messages_created = 0

    # First, delete existing messages for this session to avoid duplicates
    existing_count = ChatMessage.objects.filter(session=session).count()
    if existing_count > 0:
        logger.info(f"Deleting {existing_count} existing messages for session {session.session_id}")
        ChatMessage.objects.filter(session=session).delete()

    for line in lines:
        if line.startswith("User:"):
            if (
                current_sender
                and current_message_lines
                and save_message(session, current_sender, "\n".join(current_message_lines))
            ):
                messages_created += 1
            current_sender = "User"
            current_message_lines = [line.replace("User:", "").strip()]
        elif line.startswith("Assistant:"):
            if (
                current_sender
                and current_message_lines
                and save_message(session, current_sender, "\n".join(current_message_lines))
            ):
                messages_created += 1
            current_sender = "Assistant"
            current_message_lines = [line.replace("Assistant:", "").strip()]
        elif current_sender:
            current_message_lines.append(line.strip())

    # Save the last message
    if (
        current_sender
        and current_message_lines
        and save_message(session, current_sender, "\n".join(current_message_lines))
    ):
        messages_created += 1

    logger.info(f"Created {messages_created} messages for session {session.session_id}")
    return messages_created


def save_message(session, sender, message_text):
    """Save a message for a chat session.

    Args:
        session: The ChatSession object
        sender: The sender of the message ("User" or "Assistant")
        message_text: The message text, which may contain HTML

    Returns:
        bool: True if message was created, False otherwise
    """
    if not message_text.strip():
        return False

    try:
        # Create a CSS sanitizer with allowed CSS properties
        css_sanitizer = CSSSanitizer(
            allowed_css_properties=[
                "color",
                "background-color",
                "font-family",
                "font-size",
                "font-weight",
                "font-style",
                "text-decoration",
                "text-align",
                "margin",
                "margin-left",
                "margin-right",
                "margin-top",
                "margin-bottom",
                "padding",
                "padding-left",
                "padding-right",
                "padding-top",
                "padding-bottom",
                "border",
                "border-radius",
                "width",
                "height",
                "line-height",
            ]
        )

        # Sanitize HTML content before saving if necessary
        safe_html = bleach.clean(
            message_text,
            tags=[
                "b",
                "i",
                "u",
                "em",
                "strong",
                "a",
                "br",
                "p",
                "ul",
                "ol",
                "li",
                "span",
                "div",
                "pre",
                "code",
                "blockquote",
            ],
            attributes={
                "a": ["href", "title", "target"],
                "span": ["style", "class"],
                "div": ["style", "class"],
                "p": ["style", "class"],
                "pre": ["style", "class"],
            },
            css_sanitizer=css_sanitizer,
            strip=True,
        )

        ChatMessage.objects.create(
            session=session,
            sender=sender,
            message=message_text,
            safe_html_message=safe_html,
        )
        logger.debug(f"Stored message for session {session.session_id} from {sender}")
        return True
    except Exception as e:
        logger.error(f"Error saving message for session {session.session_id}: {e}", exc_info=True)
        return False
