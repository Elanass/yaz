# Surgify Visual Assets

This directory contains visual assets for the production README:

## Required Assets (Placeholders)

### case-list.png
![Case List Screenshot](case-list-placeholder.png)
- Shows the case management interface
- Real-time status indicators
- Collaboration features

### analytics.gif  
![Analytics Dashboard Animation](analytics-placeholder.gif)
- Interactive charts and metrics
- Survival analysis visualization
- Protocol comparison charts

### deliverable.pdf
![Sample Report Preview](deliverable-placeholder.png)
- Professional PDF report sample
- Multi-audience formatting
- Clinical insights and recommendations

### live-edit.gif
![Live Collaboration Animation](live-edit-placeholder.gif)  
- CRDT synchronization demo
- Real-time peer indicators
- Conflict resolution visualization

## Production Notes

For the production deployment, these placeholder images should be replaced with:
1. **Screenshots** of the actual Surgify dashboard and interfaces
2. **Animated GIFs** showing real user interactions
3. **PDF samples** generated from the deliverable system
4. **Screen recordings** of the collaboration features

## Asset Generation

Use these commands to generate real assets:

```bash
# Generate dashboard screenshot
surgify-enhanced demo quick --open-browser
# Then take screenshot of dashboard.html

# Generate sample reports
surgify-enhanced tasks run deliver_practitioner --file sample_data.csv

# Record collaboration demo
# (Requires P2P/CRDT implementation)
```
