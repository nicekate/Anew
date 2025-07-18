# OpenSauce 2025 Conference Schedule

A beautiful, interactive web application displaying the complete schedule for OpenSauce 2025 conference.

## Features

- 📅 **Complete 3-Day Schedule** - Friday (Industry Day), Saturday (Maker Day), Sunday (Creator Day)
- 🎨 **Modern UI Design** - Responsive design with gradient backgrounds and smooth animations
- 📱 **Mobile Friendly** - Optimized for all device sizes
- 🔍 **Search Functionality** - Find sessions by title, speaker, or description
- 📊 **Session Details** - Click any session for detailed information in a modal
- 📥 **ICS Export** - Export individual sessions or the complete schedule to your calendar
- ⚡ **Fast Loading** - Embedded data for instant access

## Data

The schedule data was scraped from the official OpenSauce website using Playwright and contains:

- **29 total sessions** across 3 days
- **Detailed session information** including time, venue, speakers, and descriptions
- **Notable speakers** including NASA Astronaut Matthew Dominick, YouTube team members, and popular creators

## Technology Stack

- **HTML5** - Semantic markup
- **CSS3** - Modern styling with flexbox, gradients, and animations
- **Vanilla JavaScript** - No frameworks, pure JS for performance
- **Font Awesome** - Icons
- **Google Fonts** - Inter font family

## Usage

Simply open `index.html` in any modern web browser. The application works entirely client-side with no server requirements.

### Calendar Export

- Click "Export All to Calendar" to download the complete schedule
- Click any session and then "Add to Calendar" to export individual sessions
- ICS files are compatible with Google Calendar, Apple Calendar, Outlook, and other calendar applications

## Development

The application consists of:

- `index.html` - Main HTML structure
- `styles.css` - All styling and responsive design
- `script.js` - Application logic and functionality
- `data.js` - Embedded schedule data
- `opensauce_2025_complete_agenda.json` - Original JSON data file

## License

This project is created for educational and informational purposes. The schedule data belongs to OpenSauce conference organizers.

---

Created with ❤️ by Augment Agent
