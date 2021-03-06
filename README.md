![landing page](./static/img/app-landing-page.png)

## About

Canvas Syllabus Scraper is a web application designed for students enrolled in courses on the learning management system [Canvas](https://www.instructure.com/canvas). It alleviates the tedious process of manually entering in tasks from Canvas into your personal task management system[^1] at the beginning of every quarter/semester.

Upon entering the URL for a course's syllabus page on Canvas and selecting a task management system, the app will scrape the syllabus content and output a CSV that can be directly imported into the specified task management system. The CSV contains the task name and due date for every task on the syllabus.

Please refer to this video for a detailed walkthrough of the scrape, download, and import steps: [https://www.youtube.com/watch?v=ztIKfVjSNU8](https://www.youtube.com/watch?v=ztIKfVjSNU8).

[^1]: Currently, only Todoist and Asana are supported.

## Demo

The application is hosted on Heroku. Click [here](https://canvas-syllabus-scraper.herokuapp.com/) to access the live demo.
