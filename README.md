# django-parallel-test

Django test runner to run a test suite across different machines.

It supports any CI system, like Heroku CI, Jenkins, Travis etc.

## Quickstart

To run the test suite on machine 1 out of a total 3, run the following:

```shell
pip install django-parallel-test

CI_NODE_INDEX=0 CI_NODE_TOTAL=3 python manage.py test --testrunner=django_parallel_test.ParallelRunner
```

### Heroku

Additional steps are needed for Heroku to enable parallel dynos.

- Update `app.json`, to add the quantity of dynos you want to run the tests on.

To run your tests on 3 dynos in parallel, your config will look something like
the following.

```json
...
  "test": {
    "formation": {
      "test": {
        "quantity": 3,
      }
    },
    "scripts": {
      "test": "python manage.py test --testrunner=django_parallel_test.ParallelRunner",
    }
  }
...
```

Heroku already adds the config vars `CI_NODE_INDEX`_ and `CI_NODE_TOTAL`, so
you do not need to add it explicitly

- Commit and push to watch it in action!

![Heroku CI](/images/heroku-ci.png)

### References

- [Heroku CI Parallel Test Runs](https://devcenter.heroku.com/articles/heroku-ci-parallel-test-runs)
- [Heroku CI Updates: Parallel Tests, CI API, and Automated UAT](https://blog.heroku.com/ci-parallel-tests)

## Other CI

- You can add the environment variables to your settings.py instead

```python
TEST_RUNNER = "django_parallel_test.ParallelRunner"  # or using --runner param
CI_NODE_TOTAL = os.environ.get("CI_NODE_TOTAL", 1)  # total number of CI dynos
CI_NODE_INDEX = os.environ.get("CI_NODE_INDEX", 0)  # index of the current dyno
```
