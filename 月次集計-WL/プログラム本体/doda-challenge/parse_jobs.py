#!/usr/bin/env python3
"""
Parse doda-challenge.txt and convert to CSV
"""
import csv
import re
from html.parser import HTMLParser


class JobParser(HTMLParser):
    """HTML parser to extract job information"""

    def __init__(self):
        super().__init__()
        self.jobs = []
        self.current_job = {}
        self.current_tag = None
        self.current_section = None
        self.capture_text = False
        self.text_buffer = []

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        attrs_dict = dict(attrs)

        # Start of a new job posting
        if tag == 'div' and attrs_dict.get('class') == 'css-olovi':
            if self.current_job:
                self.jobs.append(self.current_job)
            self.current_job = {
                '社名': '',
                '職種': '',
                '雇用形態': '',
                '仕事内容': '',
                '勤務地': '',
                '給与': '',
                '事業内容': '',
                '詳細URL': '',
                '特徴': []
            }

        # Company name
        elif tag == 'h2' and self.current_job is not None:
            self.capture_text = True
            self.text_buffer = []
            self.current_section = 'company'

        # Job title
        elif tag == 'div' and attrs_dict.get('class') == 'pr' and self.current_job is not None:
            self.capture_text = True
            self.text_buffer = []
            self.current_section = 'title'

        # Employment type
        elif tag == 'li' and attrs_dict.get('class') == 'employmentType' and self.current_job is not None:
            self.capture_text = True
            self.text_buffer = []
            self.current_section = 'employment'

        # Job details sections
        elif tag == 'h3':
            self.capture_text = True
            self.text_buffer = []
            self.current_section = 'h3'

        # Job details content
        elif tag == 'dt' and self.current_job is not None:
            self.capture_text = True
            self.text_buffer = []
            self.current_section = 'dt'

        # Detail URL
        elif tag == 'a' and self.current_job is not None:
            href = attrs_dict.get('href', '')
            if '/challenge/JobSearchDetail/' in href:
                self.current_job['詳細URL'] = href

        # Features/tags
        elif tag == 'li' and self.current_job is not None:
            self.capture_text = True
            self.text_buffer = []
            self.current_section = 'feature'

    def handle_data(self, data):
        if self.capture_text:
            self.text_buffer.append(data.strip())

    def handle_endtag(self, tag):
        if self.capture_text and self.text_buffer:
            text = ' '.join(filter(None, self.text_buffer))

            if self.current_section == 'company' and tag == 'h2':
                self.current_job['社名'] = text

            elif self.current_section == 'title' and tag == 'div':
                self.current_job['職種'] = text

            elif self.current_section == 'employment' and tag == 'li':
                self.current_job['雇用形態'] = text

            elif self.current_section == 'h3' and tag == 'h3':
                self.last_h3 = text

            elif self.current_section == 'dt' and tag == 'dt':
                if hasattr(self, 'last_h3'):
                    if '仕事内容' in self.last_h3:
                        self.current_job['仕事内容'] = text
                    elif '勤務地' in self.last_h3:
                        self.current_job['勤務地'] = text
                    elif '給' in self.last_h3 and '与' in self.last_h3:
                        self.current_job['給与'] = text
                    elif '事業内容' in self.last_h3:
                        self.current_job['事業内容'] = text

            elif self.current_section == 'feature' and tag == 'li':
                if '特徴' in self.current_job and text and text not in ['新着', 'おすすめ']:
                    self.current_job['特徴'].append(text)

            self.capture_text = False
            self.text_buffer = []

    def get_jobs(self):
        """Return all parsed jobs"""
        # Add last job if exists
        if self.current_job and self.current_job.get('社名'):
            self.jobs.append(self.current_job)
        return self.jobs


def parse_html_file(file_path):
    """Parse HTML file and extract job data"""
    parser = JobParser()

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        parser.feed(content)

    return parser.get_jobs()


def save_to_csv(jobs, output_file):
    """Save job data to CSV file"""
    if not jobs:
        print("No jobs found to export")
        return

    # Prepare data for CSV
    rows = []
    for job in jobs:
        row = {
            '社名': job['社名'],
            '職種': job['職種'],
            '雇用形態': job['雇用形態'],
            '仕事内容': job['仕事内容'],
            '勤務地': job['勤務地'],
            '給与': job['給与'].replace('<br>', ' ').replace('\n', ' '),
            '事業内容': job['事業内容'][:100] + '...' if len(job['事業内容']) > 100 else job['事業内容'],
            '特徴': '、'.join(job['特徴']),
            '詳細URL': job['詳細URL']
        }
        rows.append(row)

    # Write to CSV
    fieldnames = ['社名', '職種', '雇用形態', '仕事内容', '勤務地', '給与', '事業内容', '特徴', '詳細URL']

    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✓ {len(rows)} jobs exported to {output_file}")


def main():
    input_file = 'doda-challenge.txt'
    output_file = 'doda-jobs.csv'

    print(f"Parsing {input_file}...")
    jobs = parse_html_file(input_file)

    print(f"Found {len(jobs)} jobs")

    print(f"Saving to {output_file}...")
    save_to_csv(jobs, output_file)

    print("Done!")


if __name__ == '__main__':
    main()
