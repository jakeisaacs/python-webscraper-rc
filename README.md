# Python Webscraper - Royal Caribbean Cruises
This is a simple web scraper to track specific amenities linked to my upcoming cruise.
The lowest and most recent prices being tracked are stored in a csv.
If a lower price is found, an email is sent to me and any added recipients.
The web scraper uses Selenium due to RC having a dynamic website that injects html
after fully loading the page. I use a .env file to insert my booking ID, sail date, ship code, and email information. 
The web scraper could be made more robust by using dynamic url routing with an array of desired amenities, but I only needed to track 3 items.
I've set up a dockerfile to easily deploy to a VM or a service like Google Cloud Run. It's a bit overkill when using Windows Task Scheduler and running locally, though.

## Github Actions
This repository has been setup to run twice a day through Github Actions. Github Actions creates a Docker volume, builds the Docker image, runs the first Docker container to executre the code, and runs the second Docker container interactively to extract the outputs. Afterwards, the rc_log and rc_prices files are committed and pushed back to the repository. This process could probably be slightly simplified by moving the Selenium download and Python execution into Github actions. Though, the Dockerfile was already created and I figured I'd find a way to use it!!  
