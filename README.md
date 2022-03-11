## TODO

- [x] Add styling (Bootstrap?)
  - [x] Remove Bootstrap and self-style form page
- [x] Add 'About' page
- [x] Add processing for Asana
  - [ ] Allow user to enter assignee (update cache) #asana-assignee branch
- [ ] Refactor code
- [x] Add loading spinner
- [ ] Error management
  - [x] Check if URL is valid
  - [x] Force browser to wait until table loads (HIGH PRIORITY)
    ```html
    <tr>
      <td scope="row">
        <img src="/images/ajax-reload-animated.gif" />
      </td>
    </tr>
    ```
- [x] Create expect outputs for all available OSU CS syllabus pages
  - [x] CS325 (OK)
  - [x] CS271 (OK)
  - [x] CS261 (OK)
  - [x] CS225 (OK)
  - [x] CS372 (OK)
  - [x] CS162 (OK)
  - [x] CS340 (OK)
  - [x] CS344 (OK)
  - [x] CS361 (OK)
  - [x] CS290 (OK)
- [x] Fix bug(s) that causes discrepant outputs in above courses
- [ ] Test against non-OSU courses
  - [ ] Address instances where date range is given in 'Due' column (e.g. "6:15pm to 9:15pm" in https://canvas.northwestern.edu/courses/7060/assignments/syllabus)
- [ ] Display tasks to user prior to download
- [x] Deploy to Heroku
