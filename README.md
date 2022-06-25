![landing page](./static/img/app-landing-page.png)

## About

Canvas Syllabus Scraper is a web application designed for students enrolled in courses on the learning management system [Canvas](https://www.instructure.com/canvas). It alleviates the tedious process of manually entering in tasks from Canvas into your task management systems at the beginning of every quarter/semester. Upon entering the URL for a course's syllabus page on Canvas and selecting a task management system, the app will scrape the syllabus content and output a CSV that can be directly imported into the specified task management system[^1]. The CSV contains the task name and due date for every task on the syllabus.

[^1]Currently, only Todoist and Asana are supported.

## Demo

The application is hosted on Heroku. Click [here](https://canvas-syllabus-scraper.herokuapp.com/) to access the live demo.

## Todo

- [ ] Test against non-OSU courses
- [ ] Address instances where date range is given in 'Due' column (e.g. "6:15pm to 9:15pm" in https://canvas.northwestern.edu/courses/7060/assignments/syllabus)
- [ ] Allow user to enter assignee #asana-assignee branch
- [ ] Implement caching system
- [ ] Display tasks to user prior to download
- [ ] Add support for other todo apps
  - [ ] Microsoft To Do
  - [ ] TickTick
  - [ ] Things 3
