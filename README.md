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
  - [ ] Force browser to wait until table loads
    ```html
    <tr>
      <td scope="row">
        <img src="/images/ajax-reload-animated.gif" />
      </td>
    </tr>
    ```
- [x] Create expect outputs for all available OSU CS syllabus pages
  - [x] CS325 (3 dates off)
  - [x] CS271 (3 dates off)
  - [x] CS261 (OK)
  - [x] CS225 (OK)
  - [x] CS372 (OK)
  - [x] CS162 (4 dates off & bug for syllabus quiz date)
  - [x] CS340 (3 dates off)
  - [x] CS344 (3 dates off)
  - [x] CS361 (OK)
  - [x] CS290 (OK)
- [ ] Fix bug(s) that causes discrepant outputs in above courses (HIGH PRIORITY)
- [ ] Test against non-OSU courses
- [ ] Display tasks to user prior to download
- [ ] Deploy to Heroku
