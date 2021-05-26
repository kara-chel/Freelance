#!/usr/bin/env python3

from scrapy import cmdline

if __name__ == '__main__':
    cmdline.execute("scrapy crawl old_tender".split())
