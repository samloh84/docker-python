#!/usr/bin/env python2

import os, sys, json, re, urlparse, errno, time, argparse
from datetime import datetime, timedelta
import yaml, semver, requests, grequests, jinja2
from bs4 import BeautifulSoup

PYTHON_DISTRIBUTION_URL = "https://www.python.org/ftp/python/"
PYTHON_RELEASES_URL = "https://www.python.org/downloads/release/"


def http_get(url, headers=None):
    return requests.get(url, headers=headers)


def http_multiget(urls, headers=None):
    return zip(urls, grequests.map([grequests.get(url, headers=headers) for url in urls]))


def list_docker_hub_image_tags(repository):
    url = "https://hub.docker.com/v2/repositories/" + repository + "/tags"
    request_headers = {'Accept': 'application/json'}

    tags = []

    while url is not None:
        response_data = http_get(url, headers=request_headers).json()
        tags += response_data["results"]
        url = response_data["next"]

    return tags


def list_python_versions():
    python_distribution_html = requests.get(PYTHON_DISTRIBUTION_URL).text
    python_distribution_soup = BeautifulSoup(python_distribution_html, 'html.parser')

    version_pattern = re.compile('^(\d+\.\d+\.\d+)/$')

    python_version_links = python_distribution_soup.find_all('a', href=version_pattern)

    python_versions = {}
    for python_version_link in python_version_links:
        python_version = version_pattern.match(python_version_link['href']).group(1)
        python_version_url = urlparse.urljoin(PYTHON_DISTRIBUTION_URL, python_version_link['href'])

        python_versions[python_version] = {'link': python_version_url}

    return python_versions


def list_python_version_files(python_versions):
    def parse_html(python_version_url, python_version_html, python_release_html):
        patterns = {
            'signatures': re.compile('^Python-\d+\.\d+\.\d+(\.tar\.xz\.asc|\.tgz\.asc)$'),
            'source': re.compile('^Python-\d+\.\d+\.\d+(\.tar\.xz|\.tgz)$')
        }

        python_version_soup = BeautifulSoup(python_version_html, 'html.parser')
        python_release_soup = BeautifulSoup(python_release_html, 'html.parser')

        python_version_data = {}

        for key, pattern in patterns.iteritems():
            python_version_data[key] = {}
            python_version_file_links = python_version_soup.find_all('a', href=pattern)
            for python_version_file_link in python_version_file_links:
                filename = python_version_file_link['href']
                file_extension = pattern.match(filename).group(1)
                python_version_file_url = urlparse.urljoin(python_version_url, python_version_file_link['href'])

                python_version_data[key][file_extension] = {
                    'filename': filename,
                    'url': python_version_file_url,
                }

        for extension, source_file in python_version_data['source'].iteritems():
            release_link = python_release_soup.find('a', href=source_file['url'])
            md5sum = release_link.find_parent('tr').find_all('td')[3].text
            python_version_data['source'][extension]['md5sum'] = md5sum

        return python_version_data

    python_release_urls = map(
        lambda version: urlparse.urljoin(PYTHON_RELEASES_URL, 'python-' +
                                         re.sub('[^\d]+', '', version)) + '/', python_versions)

    python_version_urls = map(lambda version: urlparse.urljoin(PYTHON_DISTRIBUTION_URL, version + '/'),
                              python_versions)

    python_version_responses = http_multiget(python_version_urls)
    python_release_responses = http_multiget(python_release_urls)
    python_version_html = map(lambda response_tuple: response_tuple[1].text, python_version_responses)
    python_release_html = map(lambda response_tuple: response_tuple[1].text, python_release_responses)
    print(python_version_urls)

    version_data = {}
    for python_version, python_version_url, python_version_html, python_release_html in zip(python_versions,
                                                                                            python_version_urls,
                                                                                            python_version_html,
                                                                                            python_release_html):
        version_data[python_version] = parse_html(python_version_url, python_version_html, python_release_html)
    return version_data


def filter_latest_major_versions(versions, min_ver=None, max_ver=None):
    major_versions = {}

    latest_versions = []

    for version in versions:
        version_info = semver.parse_version_info(version)

        if min_ver is not None and not semver.match(version, min_ver):
            continue

        if max_ver is not None and not semver.match(version, max_ver):
            continue

        major_version = str(version_info.major)
        minor_version = str(version_info.minor)
        current_major_version = major_versions.get(major_version)

        if current_major_version is None:
            major_versions[major_version] = {}
        else:
            current_minor_version = current_major_version.get(minor_version)
            if current_minor_version is None or semver.compare(version, current_minor_version) > 0:
                major_versions[major_version][minor_version] = version

    for minor_version in major_versions.values():
        latest_versions += minor_version.values()

    return latest_versions


def load_file(filename):
    filename = os.path.abspath(filename)
    with open(filename, 'r') as f:
        return f.read()


def load_yaml(filename):
    return yaml.safe_load(load_file(filename))


def write_file(filename, data):
    filename = os.path.abspath(filename)
    file_dir = os.path.dirname(filename)
    mkdirp(file_dir)
    with open(filename, 'w') as f:
        f.write(data)


def write_yaml(filename, data):
    write_file(filename, yaml.safe_dump(data))


def datetime_to_timestamp(date=None):
    if date is None:
        date = datetime.now()
    return int(time.mktime(date.timetuple()))


def timestamp_to_datetime(timestamp):
    if timestamp is None or timestamp == "":
        return None
    return datetime.fromtimestamp(int(timestamp))


def mkdirp(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass


def load_python_data(config, data_file, force_update=False, update_all_versions=False):
    current_datetime = datetime.now()
    current_timestamp = datetime_to_timestamp(current_datetime)

    python_data = {'versions': {}}
    last_updated = None
    python_data_updated = False

    try:
        if os.path.isfile(data_file):
            python_data = load_yaml(data_file)
            last_updated = timestamp_to_datetime(python_data['last_updated'])
    except:
        pass

    update = force_update or last_updated is None or last_updated + timedelta(days=1) <= current_datetime

    if update:
        versions = list_python_versions()
        for version in versions:
            if python_data['versions'].get(version) is None:
                python_data['versions'][version] = {}
        python_data_updated = True
    else:
        versions = python_data['versions'].keys()

    latest_major_versions = filter_latest_major_versions(versions, config.get('min_version'), config.get('max_version'))

    if update_all_versions:
        versions_to_update = versions
    else:
        versions_to_update = [version for version in latest_major_versions if
                              force_update or python_data['versions'][version].get('files') is None]

    if versions_to_update:
        python_version_files = list_python_version_files(versions_to_update)
        for version, version_files in python_version_files.iteritems():
            if python_data['versions'][version].get('files') is None:
                python_data['versions'][version]['files'] = {}
            python_data['versions'][version]['files'].update(version_files)
        python_data_updated = True

    if python_data_updated:
        python_data['last_updated'] = datetime_to_timestamp()
        write_yaml(data_file, python_data)
        print ("Updated " + data_file)

    return python_data, latest_major_versions


def render_dockerfiles(config, python_data, latest_major_versions, force_update=False):
    jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.abspath('templates')))

    for base_repository in config['base_repositories']:
        base_repository_tags = [base_repository_tag['name'] for base_repository_tag in
                                list_docker_hub_image_tags(base_repository) if base_repository_tag['name'] != 'latest']

        base_os = base_repository[base_repository.rfind('/') + 1:]

        makefile_template = jinja2_env.select_template(['Makefile.' + base_os + '.j2', 'Makefile.j2'])

        for base_repository_tag in base_repository_tags:
            base_image_name = base_repository + ':' + base_repository_tag
            tag_suffix = base_os + base_repository_tag

            for version in latest_major_versions:

                dockerfile_template = jinja2_env.select_template([
                    'Dockerfile.' + 'python' + str(semver.parse_version_info(version).major) + '.' + base_os + '.j2',
                    'Dockerfile.' + base_os + '.j2', 'Dockerfile.j2'])

                image_tags = [version, version + '-' + tag_suffix]
                dockerfile_context = os.path.join(os.getcwd(), version, tag_suffix)

                dockerfile_path = os.path.join(dockerfile_context, 'Dockerfile')
                makefile_path = os.path.join(dockerfile_context, 'Makefile')

                dockerfile_exists = os.path.exists(dockerfile_path)
                makefile_exists = os.path.exists(makefile_path)

                if force_update or not dockerfile_exists or not makefile_exists:
                    render_data = {
                        'version': version,
                        'repository_name': config['repository_name'],
                        'base_os': base_os,
                        'base_image_name': base_image_name,
                        'tag_suffix': tag_suffix,
                        'dockerfile_context': dockerfile_context,
                        'image_tags': image_tags
                    }

                    render_data.update(python_data['versions'][version])

                    try:
                        if force_update or not dockerfile_exists:
                            write_file(dockerfile_path, dockerfile_template.render(render_data))
                            print 'Generated ' + dockerfile_path
                        if force_update or not makefile_exists:
                            write_file(makefile_path, makefile_template.render(render_data))
                            print 'Generated ' + makefile_path
                    except BaseException as err:
                        print(version)
                        print(err)


def main(argv):
    parser = argparse.ArgumentParser(description='Updates Python data file with version URLs and Dockerfiles.')
    parser.add_argument('--data-file', nargs=1, dest='data_file', default=os.path.abspath('python.yml'))
    parser.add_argument('--config-file', nargs=1, dest='config_file', default=os.path.abspath('config.yml'))
    parser.add_argument('-f', '--force-update', dest='force_update', action='store_true')
    parser.add_argument('-a', '--update-all', dest='update_all', action='store_true')

    parsed_args = vars(parser.parse_args())

    config_file = parsed_args.get('config_file')
    data_file = parsed_args.get('data_file')
    force_update = parsed_args.get('force_update')
    update_all = parsed_args.get('update_all')

    config = load_yaml(config_file)

    python_data, latest_major_versions = load_python_data(config, data_file, force_update, update_all)
    render_dockerfiles(config, python_data, latest_major_versions, force_update)


if __name__ == '__main__':
    main(sys.argv)
