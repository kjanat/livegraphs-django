# LiveGraphs Project TODO

## Dashboard UI Improvements

### Responsiveness

- [ ] Fix dashboard graphs scaling/adjustment when zooming (currently requires page refresh)

### Theming

- [x] Add dark mode/light mode toggle
- [x] Fix dark mode implementation issues:
  - [x] Make charts display properly in dark mode
  - [x] Fix the footer not changing color in dark mode
  - [x] Adjust the sidebar nav-link styling for dark mode
  - [x] Make the navbar have a different background color from the body in dark mode
  - [x] Make theme toggle automatically detect and respect the user's system preference
  - [x] Fix inconsistency between system dark mode preference and manual toggle
  - [x] Ensure charts properly update in both scenarios (system preference and manual toggle)
- [x] Implement smooth theme transitions
- [ ] Add Notso AI branding elements
- [ ] Implement responsive table design (reduce rows to fit screen)

### Data Export

- [x] Implement multi-format export functionality
  - [x] CSV format
  - [ ] Excel format
  - [x] JSON format
  - [ ] XML format
  - [ ] HTML format
  - [ ] PDF format
- [ ] Create dropdown menu for export options
- [x] Make export data section collapsible (folded by default)
- [x] Add company name, date and timestamp to exported filenames
- [ ] Update [data view](dashboard_project/templates/dashboard/partials/data_table.html) to show maximum 10 rows by default, with a "Show more" button to expand to 50 rows, or "Show all" to display all rows

## Admin Interface Enhancements

### Company Management

- [ ] Add company logo upload functionality
- [ ] Add direct CSV download button for each company (superusers only)
  - [ ] Include company name, date and timestamp in filename
- [ ] Add UI for customizing CSV column names

## Data Integration

### External Data Sources

- [ ] Implement periodic data download from external API
  - Source: <https://proto.notso.ai/jumbo/chats>
  - Authentication: Basic Auth
  - Credentials: [stored securely]
  - An example of the data structure can be found in [jumbo.csv](examples/jumbo.csv)
    - The file that the endpoint returns is a CSV file, but the file is not a standard CSV file. It has a different structure and format:
    - The header row is missing, it is supposed to be `session_id,start_time,end_time,ip_address,country,language,messages_sent,sentiment,escalated,forwarded_hr,full_transcript,avg_response_time,tokens,tokens_eur,category,initial_msg,user_rating`
  - [ ] The coupling of endpoint to the company and the authentication method should be handled in the backend and the superuser should be able to change it.
  - [ ] The data should be stored in the database and the dashboard should be updated with the new data.
  - [ ] The csv also contains a column with full_transcript, which is a uri to a txt file, encoded in utf-8. The txt file is a raw transcript of the chat.
    - [ ] The txt file should be downloaded, parsed and stored in the database.
    - An example of such txt file can be found in [132f3a8c-3ba5-4d89-ae04-cd83f1bc5272.txt](examples/132f3a8c-3ba5-4d89-ae04-cd83f1bc5272.txt)
    - Note that the User and Assistant messages can be multiline and can contain html, which should be safely handled, and if safe, rendered in the frontend.
- [ ] Add scheduling options for data refresh
- [ ] Add UI button to trigger manual data refresh

## Technical Debt

### Performance Optimization

- [ ] Profile and optimize dashboard rendering
- [ ] Implement lazy loading for dashboard elements

### Testing

- [ ] Add unit tests for export functionality
- [ ] Add integration tests for data import process
