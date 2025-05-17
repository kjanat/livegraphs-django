# LiveGraphs Project TODO

## Dashboard UI Improvements

### Responsiveness

- [ ] Fix dashboard graphs scaling/adjustment when zooming (currently requires page refresh)

### Theming

- [ ] Add dark mode/light mode toggle
- [ ] Add Notso AI branding elements
- [ ] Implement responsive table design (reduce rows to fit screen)

### Data Export

- [ ] Implement multi-format export functionality
  - [ ] CSV format
  - [ ] Excel format
  - [ ] JSON format
  - [ ] XML format
  - [ ] HTML format
  - [ ] PDF format
- [ ] Create dropdown menu for export options
- [ ] Make export data section collapsible (folded by default)
- [ ] Add company name, date and timestamp to exported filenames

## Admin Interface Enhancements

### Company Management

- [ ] Add company logo upload functionality
- [ ] Add direct CSV download button for each company (superusers only)
  - [ ] Include company name, date and timestamp in filename
- [ ] Add UI for customizing CSV column names

## Data Integration

### External Data Sources

- [ ] Implement periodic data download from external API
  - [ ] Source: <https://proto.notso.ai/XY/chats>
  - [ ] Authentication: Basic Auth
  - [ ] Credentials: [stored securely]
- [ ] Add scheduling options for data refresh

## Technical Debt

### Performance Optimization

- [ ] Profile and optimize dashboard rendering
- [ ] Implement lazy loading for dashboard elements

### Testing

- [ ] Add unit tests for export functionality
- [ ] Add integration tests for data import process
