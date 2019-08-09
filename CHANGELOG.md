# Change Log

The following list provides a brief overview of all features, bug fixes, and
breaking changes as part of Perimeterator releases.

## 0.3.0

### 🤘Features

* Adds AWS Elasticsearch Service support.
* Single sourced versioning (`perimeterator.__version__`).
* Bumped `boto3` version to latest.

### 🐛Bug Fixes

* Fixed broken paths to `scripts` in `setup.py`.
* Documentation update to indicate first `enumerator` run may need to be run
  manually, or it could take 24-hours for the first run to be executed. This
  is due to the `rate(24 hours)` CloudWatch Events schedule.

### 💥Breaking Changes

* Nmap scanner now defaults to TCP only scans to greatly speed up scanning.
* Changed installation paths inside `scanner` container. However, as the
  container entrypoint was updated to reflect new paths, no impact should be
  seen for the vast majority of users.

## 0.2.0

### 🤘Features

* Added paging to enumerators in order to support accounts with a large
  number of resources.

### 🐛Bug Fixes

* N/A

### 💥Breaking Changes

* N/A

## 0.1.0

### 🤘Features

* Initial Release.

### 🐛Bug Fixes

* N/A

### 💥Breaking Changes

* N/A
