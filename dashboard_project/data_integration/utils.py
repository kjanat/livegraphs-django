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

            # Parse date fields with multiple format support
            start_time = None
            end_time = None

            # List of date formats to try
            date_formats = [
                "%d.%m.%Y %H:%M:%S",  # European format: DD.MM.YYYY HH:MM:SS
                "%Y-%m-%d %H:%M:%S",  # ISO format: YYYY-MM-DD HH:MM:SS
                "%m/%d/%Y %H:%M:%S",  # US format: MM/DD/YYYY HH:MM:SS
                "%Y-%m-%dT%H:%M:%S",  # ISO format with T separator
                "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO format with milliseconds and Z
            ]

            # Try to parse start_time with multiple formats
            for date_format in date_formats:
                try:
                    start_time = make_aware(datetime.strptime(data["start_time"], date_format))
                    break
                except (ValueError, TypeError):
                    continue

            # Try to parse end_time with multiple formats
            for date_format in date_formats:
                try:
                    end_time = make_aware(datetime.strptime(data["end_time"], date_format))
                    break
                except (ValueError, TypeError):
                    continue

            # If we couldn't parse the dates, log an error and skip this row
            if not start_time or not end_time:
                error_msg = f"Could not parse date fields for session {data['session_id']}: start_time={data['start_time']}, end_time={data['end_time']}"
                logger.error(error_msg)
                stats["errors"] += 1
                continue

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

    This function parses a chat transcript that contains messages from both User and Assistant.
    It identifies message boundaries by looking for lines that start with common sender patterns,
    and groups all following lines until the next sender change as part of that message.

    Args:
        session: The ChatSession object
        transcript_content: The raw transcript content

    Returns:
        int: Number of messages created
    """
    # Handle empty transcripts
    if not transcript_content or transcript_content.strip() == "":
        logger.warning(f"Empty transcript received for session {session.session_id}")
        return 0

    lines = transcript_content.splitlines()
    current_sender = None
    current_message_lines = []
    messages_created = 0

    # First, delete existing messages for this session to avoid duplicates
    existing_count = ChatMessage.objects.filter(session=session).count()
    if existing_count > 0:
        logger.info(f"Deleting {existing_count} existing messages for session {session.session_id}")
        ChatMessage.objects.filter(session=session).delete()

    # Define common message patterns to detect - expanded to include more variations
    user_patterns = [
        "User:",
        "[User]:",
        "Customer:",
        "[Customer]:",
        "Client:",
        "[Client]:",
        "Human:",
        "[Human]:",
        "Me:",
        "[Me]:",
        "Question:",
        "User >",
        "Customer >",
        "User said:",
        "Customer said:",
        "User writes:",
        "User asked:",
        "User message:",
        "From user:",
        "Client message:",
        "Q:",
        "Input:",
        "Query:",
        "Person:",
        "Visitor:",
        "Guest:",
        "User input:",
        "User query:",
    ]
    assistant_patterns = [
        "Assistant:",
        "[Assistant]:",
        "Agent:",
        "[Agent]:",
        "Bot:",
        "[Bot]:",
        "AI:",
        "[AI]:",
        "ChatGPT:",
        "[ChatGPT]:",
        "System:",
        "[System]:",
        "Support:",
        "[Support]:",
        "Answer:",
        "Assistant >",
        "Bot >",
        "Assistant said:",
        "Assistant writes:",
        "AI responded:",
        "LLM:",
        "[LLM]:",
        "Response:",
        "A:",
        "Output:",
        "AI output:",
        "Model:",
        "[Model]:",
        "Assistant message:",
        "From assistant:",
        "Bot response:",
        "AI says:",
        "NotsoAI:",
        "[NotsoAI]:",
        "Notso:",
        "[Notso]:",
    ]

    # Function to save current message before starting a new one
    def save_current_message():
        nonlocal current_sender, current_message_lines, messages_created
        if current_sender and current_message_lines:
            message_text = "\n".join(current_message_lines)
            # Only save if there's actual content (not just whitespace)
            if message_text.strip() and save_message(session, current_sender, message_text):
                messages_created += 1
                logger.debug(f"Saved {current_sender} message with {len(current_message_lines)} lines")

    # Initial scan to detect format type and potential message boundaries
    has_recognized_patterns = False
    potential_timestamps = []
    timestamp_pattern_count = 0

    # Regex patterns for common timestamp formats
    import re

    timestamp_patterns = [
        r"^\[\d{2}:\d{2}:\d{2}\]",  # [HH:MM:SS]
        r"^\[\d{2}:\d{2}\]",  # [HH:MM]
        r"^\(\d{2}:\d{2}:\d{2}\)",  # (HH:MM:SS)
        r"^\(\d{2}:\d{2}\)",  # (HH:MM)
        r"^\d{2}:\d{2}:\d{2} -",  # HH:MM:SS -
        r"^\d{2}:\d{2} -",  # HH:MM -
        r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",  # YYYY-MM-DD HH:MM:SS
    ]

    # First pass: detect format and message boundaries
    for i, line in enumerate(lines):
        line_stripped = line.strip()

        # Check for standard message patterns
        if any(line_stripped.startswith(pattern) for pattern in user_patterns + assistant_patterns):
            has_recognized_patterns = True

        # Check for timestamp patterns that might indicate message boundaries
        for pattern in timestamp_patterns:
            if re.match(pattern, line_stripped):
                timestamp_pattern_count += 1
                potential_timestamps.append(i)
                break

    # If no recognized patterns are found, try to intelligently split the transcript
    if not has_recognized_patterns and len(lines) > 0:
        logger.info(
            f"No standard message patterns found in transcript for session {session.session_id}. Attempting intelligent split."
        )

        # Try timestamp-based parsing if we have enough consistent timestamps
        if timestamp_pattern_count > 3 and timestamp_pattern_count > 0.2 * len(lines):
            logger.info(f"Attempting timestamp-based parsing with {timestamp_pattern_count} detected timestamps")

            # Add the end of file as a boundary
            potential_timestamps.append(len(lines))

            # Process messages between timestamps
            for i in range(len(potential_timestamps) - 1):
                start_idx = potential_timestamps[i]
                end_idx = potential_timestamps[i + 1]

                message_content = "\n".join(lines[start_idx:end_idx])
                first_line = lines[start_idx].lower()

                # Simple heuristic to identify sender
                is_user = any(
                    user_word in first_line
                    for user_word in ["user", "customer", "client", "human", "question", "query"]
                )
                is_assistant = any(
                    assistant_word in first_line
                    for assistant_word in ["assistant", "agent", "bot", "ai", "system", "support", "answer", "response"]
                )

                sender = "User" if (is_user or (not is_assistant and i % 2 == 0)) else "Assistant"

                if save_message(session, sender, message_content):
                    messages_created += 1

            logger.info(f"Created {messages_created} messages using timestamp-based parsing")
            return messages_created

        # Simple heuristic: alternate between user and assistant, with first message from user
        # Start with paragraphs (blank line separations) as message boundaries
        paragraphs = []
        current_paragraph = []

        for line in lines:
            if line.strip():
                current_paragraph.append(line)
            elif current_paragraph:  # Empty line and we have a paragraph
                paragraphs.append("\n".join(current_paragraph))
                current_paragraph = []

        # Add the last paragraph if it's not empty
        if current_paragraph:
            paragraphs.append("\n".join(current_paragraph))

        # If we have just one paragraph, try to split by sentence boundaries for very long transcripts
        if len(paragraphs) == 1 and len(paragraphs[0].split()) > 100:
            import re

            # Try to split by sentence boundaries
            text = paragraphs[0]
            # Define sentence ending patterns
            sentence_endings = r"(?<=[.!?])\s+"
            sentences = re.split(sentence_endings, text)
            # Group sentences into logical chunks (assuming alternating speakers)
            chunks = []
            current_chunk = []

            for i, sentence in enumerate(sentences):
                current_chunk.append(sentence)
                # Every 2-3 sentences or on a natural break like a question mark
                if (i % 2 == 1 and sentence.endswith("?")) or len(current_chunk) >= 3:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []

            # Add any remaining sentences
            if current_chunk:
                chunks.append(" ".join(current_chunk))

            # Save the chunks alternating between user and assistant
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    sender = "User" if i % 2 == 0 else "Assistant"
                    if save_message(session, sender, chunk):
                        messages_created += 1

            logger.info(f"Created {messages_created} messages by splitting single paragraph into sentences")
            return messages_created

        # Save messages alternating between user and assistant
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():  # Only save non-empty paragraphs
                sender = "User" if i % 2 == 0 else "Assistant"
                if save_message(session, sender, paragraph):
                    messages_created += 1

        logger.info(f"Created {messages_created} messages using intelligent split for session {session.session_id}")
        return messages_created

    # Standard processing with recognized patterns
    for line in lines:
        line_stripped = line.strip()

        # Skip empty lines at the beginning
        if not line_stripped and not current_sender:
            continue

        # Check if this line indicates a new sender
        is_user_message = any(line_stripped.startswith(pattern) for pattern in user_patterns)
        is_assistant_message = any(line_stripped.startswith(pattern) for pattern in assistant_patterns)

        if is_user_message:
            # Save previous message if any
            save_current_message()

            # Start new user message
            current_sender = "User"
            # Remove the prefix from the line
            for pattern in user_patterns:
                if line_stripped.startswith(pattern):
                    line = line[len(pattern) :].strip()
                    break
            current_message_lines = [line] if line.strip() else []
        elif is_assistant_message:
            # Save previous message if any
            save_current_message()

            # Start new assistant message
            current_sender = "Assistant"
            # Remove the prefix from the line
            for pattern in assistant_patterns:
                if line_stripped.startswith(pattern):
                    line = line[len(pattern) :].strip()
                    break
            current_message_lines = [line] if line.strip() else []
        elif current_sender:
            # Continue adding to current message
            current_message_lines.append(line)
        else:
            # If we get here with no current_sender, assume it's the start of a user message
            logger.warning(f"Found line without sender prefix: '{line}'. Assuming User message.")
            current_sender = "User"
            current_message_lines = [line]

    # Save the last message
    save_current_message()

    # Handle case with no messages parsed (possibly incorrectly formatted transcript)
    if messages_created == 0 and lines:
        logger.warning(
            f"No messages were parsed from transcript for session {session.session_id}. Using fallback parsing."
        )

        # Fallback: Just split the transcript in half, first part user, second part assistant
        mid_point = len(lines) // 2
        user_content = "\n".join(lines[:mid_point])
        assistant_content = "\n".join(lines[mid_point:])

        # Save the split messages if they have content
        if user_content.strip() and save_message(session, "User", user_content):
            messages_created += 1

        if assistant_content.strip() and save_message(session, "Assistant", assistant_content):
            messages_created += 1

        logger.info(f"Created {messages_created} messages using fallback parsing")

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
