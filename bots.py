"""Ein Set an Bots, die mein Blog für mich schreiben."""

import sys
import logging
import os
import feedparser

from datetime import datetime
from textwrap import dedent
from datetime import date
from subprocess import call, check_output, CalledProcessError
from shlex import quote
from tempfile import TemporaryDirectory
from slugify import slugify


defaulttemplate = dedent("""\
        Title: {title}
        Date: {date}
        Category: {categories}
        Tags: {tags}
        Author: {author}
        Slug: {slug}
        Status: {status}

        {body}
        """)


class GenericBot:
    config = {
        "title": "GenericBots Generic Post",
        "date": date.today().isoformat(),
        "categories": "GenericCategory",
        "tags": "GenericTag",
        "author": "GenericBot",
        "slug": "genericbots-generic-post",
        "status": "draft",
        "body": "## Generic Title\n\nGeneric Post Body",

        # String Template for blog post
        "template": defaulttemplate,

        # Timeout value: Maximum number of days since last post
        "timeout": 3
    }

    def __init__(self, name="GenericBot", config=None, check_config=False):

        self.log = logging.getLogger(__name__)
        self.log.addHandler(logging.NullHandler())

        self.log.debug("Initiating {} Instance...".format(self.__class__.__name__))

        self.name = name

        # get temporary directory and put it in config
        self.config["tempdir"] = TemporaryDirectory(dir=os.path.abspath("."))

        if config:
            self.config.update(config)
            self.log.debug("Instance-Specific config found: Default configuration updated.")

        # check for botspecific configuration
        if self.name in config:
            self.config.update(config[self.name])
            self.log.debug("Bot-specific config found: Default configuration updated.")

        if check_config:
            # check config for necessary data
            assert "feed" in self.config
            assert "repo" in self.config

    def build_post(self):
        self.log.info("Building post...")

        template = self.config["template"]

        self.config["slug"] = slugify(self.config["title"])

        post = template.format(**self.config)

        self.log.debug("Post built:\n\n{}\n\n".format(str(post)))

        return post

    def check_feed(self):

        try:
            feed = self.config["feed"]
            self.log.debug("Feed URL: {}".format(feed))
        except KeyError as e:
            self.log.error("No feed found in config!")
            self.log.error(e)

            sys.exit(-1)

        fp = feedparser.parse(feed)
        self.log.info("Checking feed...")

        # Get date of last published blog post in UTC
        last_post = fp["entries"][0].published_parsed
        self.log.debug("Last post date parsed: {}".format(last_post))

        # cast date to datetime
        last_post = datetime(*last_post[:6])

        # get current datetime in UTC
        now = datetime.utcnow()

        # compute difference
        time_since = now - last_post
        self.log.debug("Days since last blog post: {}".format(time_since.days))

        # check if time since last post is longer than timeout value
        return time_since.days > self.config["timeout"]

    def clone_repo(self, tempdir=None):
        if not tempdir:
            tempdir = self.config["tempdir"]

        repo_path = self.config["repo"]

        # check for ~/
        repo_path = os.path.expanduser(repo_path)

        # check for relative paths
        repo_path = os.path.abspath(repo_path)

        # check that repo_path points at a bare git repo or pushing will not work
        assert "HEAD" in os.listdir(repo_path)
        assert repo_path.endswith(".git")

        # clone repo to _repo dir using quoted path
        res = call(["git", "clone", quote(repo_path), tempdir.name])

        if res != 0:
            raise OSError("Could not clone repo: {}".format(repo_path))

    def write_post(self, tempdir=None):

        if not tempdir:
            tempdir = self.config["tempdir"]

        assert "content" in os.listdir(tempdir.name)

        post = self.build_post()

        content_path = os.path.join(tempdir.name, "content")

        self.log.debug("CONTENT PATH: {}".format(content_path))

        filename = self.config["date"] + "-" + self.config["slug"] + ".md"

        target = os.path.join(content_path, filename)

        self.log.debug("TARGET POST FILE: {}".format(target))

        with open(target, "w") as f:
            f.write(post)

        self.log.info("Post written.")

    def commit_post(self, tempdir=None):

        if not tempdir:
            tempdir = self.config["tempdir"]

        target = os.path.join(tempdir.name, "content")

        if os.getcwd() != tempdir.name:

            self.log.debug("Changing directory to: {}".format(tempdir.name))

            os.chdir(tempdir.name)

        self.log.info("Committing changes...")

        res = call(["git", "add", target])

        self.log.debug("Calling git: 'git add {}'\nReturn code: {}".format(target, res))

        res = call(["git", "commit", "-m", "[POST] {} added a new post: {}".format(self.name, self.config["title"])])

        self.log.debug("Calling git: 'git commit -m ...'\nReturn code: {}".format(res))

    def push_repo(self, tempdir=None):
        """Push changes to blog repo."""

        if not tempdir:
            tempdir = self.config["tempdir"]

        if os.getcwd() != tempdir.name:

            self.log.debug("Changing directory to {}.".format(tempdir.name))
            os.chdir(tempdir.name)

        assert ".git" in os.listdir(".")    # Check that we've moved into a non-bare git repo
        self.log.debug("Checked for git repo: {}".format(tempdir.name))

        self.log.debug("Trying regular 'git push'...")

        try:
            output = check_output(["git", "push"])
            self.log.debug("Output for 'git push': {}".format(output))
        except CalledProcessError as e:
            self.log.error("Push failed!", exc_info=e)
            self.log.debug("Trying gitolite admin-push...")

            try:
                output = check_output(["gl-admin-push"])
                self.log.debug("Output for 'gl-admin-push: {}".format(output))
            except CalledProcessError as e:
                self.log.error("Gitolite admin push failed", exc_info=e)
                self.log.error("Pushing failed: Remote repo unchanged!")
                self.log.error("Please check log for errors.")
                return

        self.log.info("Changed pushed successfully!")












class ImageBot(GenericBot):

    def __init__(self, name="ImageBot", config=None, check_config=False):
        GenericBot.__init__(self, name, config, check_config)

        self.config["author"] = "ImageBot"

        if check_config:
            assert "imagedir" in self.config

    def build_post(self):
        from pixelsort import randimage, all_random, half

        try:
            imgdir = self.config["imagedir"]
        except KeyError:
            imgdir = "./"


        image = randimage(imgdir)

        # aply filter


if __name__ == "__main__":
    # set up logging
    logging.basicConfig(level=logging.DEBUG)

    config = {
        "feed": "foo",
        "repo": "testy"
    }

    with TemporaryDirectory() as foo:

        gen = GenericBot(config=config)

        gen.clone_repo(foo)

        gen.write_post(foo)

        gen.commit_post(foo)

