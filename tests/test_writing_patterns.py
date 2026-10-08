"""Exercise the offline writing-atlas CLI and its provenance boundary."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / '.agents/skills/paper-craft'
ATLAS = SKILL / 'venues/writing-patterns.json'
SCRIPT = SKILL / 'scripts/validate_writing_patterns.py'


class WritingPatternTests(unittest.TestCase):
    def test_structure_pass_when_packaged_sample_is_checked(self) -> None:
        # Given the actual shipped atlas.
        # When invoking the real offline CLI.
        result = subprocess.run([sys.executable, str(SCRIPT), '--json'], capture_output=True,
                                text=True, check=False, timeout=30)
        # Then structure passes while scientific and current-rule judgments remain unknown.
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        report = json.loads(result.stdout)
        self.assertEqual(report['status'], 'PASS')
        self.assertEqual(report['scientific_validity'], 'UNKNOWN')
        self.assertEqual(report['current_rule_applicability'], 'UNKNOWN')

    def test_rejection_when_provenance_is_missing_or_contradictory(self) -> None:
        cases = ('unread', 'missing_locator', 'unread_locator', 'unknown_paper',
                 'official_requirement', 'official_recommendation', 'unknown_category',
                 'missing_scope', 'venue_wide', 'wrong_sample_size', 'false_unsampled',
                 'bad_url', 'bad_hash', 'missing_revision', 'invalid_date', 'wrong_page',
                 'wrong_venue', 'duplicate_paper', 'bad_read_status')
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temporary:
                # Given a damaged copy of a valid real atlas.
                data = json.loads(ATLAS.read_text(encoding='utf-8'))
                observation = data['observations'][0]
                paper = data['papers'][0]
                mutations = {
                    'unread': lambda: paper['read_coverage'].update(status='unread', read_at=None, locators=[]),
                    'missing_locator': lambda: observation.update(locators=[]),
                    'unread_locator': lambda: observation['locators'][0].update(section='Unread appendix'),
                    'unknown_paper': lambda: observation.update(paper_id='missing'),
                    'official_requirement': lambda: observation.update(category='official_requirement'),
                    'official_recommendation': lambda: observation.update(category='official_recommendation'),
                    'unknown_category': lambda: observation.update(category='venue_tradition'),
                    'missing_scope': lambda: observation.update(scope_limit=' '),
                    'venue_wide': lambda: observation.update(generalization='venue_wide'),
                    'wrong_sample_size': lambda: data['venues'][0].update(sample_size=10),
                    'false_unsampled': lambda: data['venues'][0].update(sampling_status='unsampled'),
                    'bad_url': lambda: paper.update(paper_url='https://user:secret@example.org/paper.pdf'),
                    'bad_hash': lambda: paper.update(pdf_sha256='UNKNOWN'),
                    'missing_revision': lambda: paper.pop('exact_revision'),
                    'invalid_date': lambda: paper['read_coverage'].update(read_at='2026-02-30'),
                    'wrong_page': lambda: observation['locators'][0].update(pdf_page=1000),
                    'wrong_venue': lambda: observation.update(venue_id='CAL'),
                    'duplicate_paper': lambda: data['papers'].append(paper),
                    'bad_read_status': lambda: paper['read_coverage'].update(status='skimmed'),
                }
                mutations[case]()
                path = Path(temporary) / 'atlas.json'
                path.write_text(json.dumps(data), encoding='utf-8')
                # When invoking the real CLI on that input.
                result = subprocess.run([sys.executable, str(SCRIPT), str(path), '--json'],
                                        capture_output=True, text=True, check=False, timeout=30)
                # Then it rejects structurally without a traceback or truth certification.
                self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
                report = json.loads(result.stdout)
                self.assertEqual(report['status'], 'FAIL')
                self.assertEqual(report['scientific_validity'], 'UNKNOWN')

    def test_explicit_sample_limits_when_reading_seeded_venues(self) -> None:
        # Given the shipped sample manifest.
        # When reading its venue coverage.
        data = json.loads(ATLAS.read_text(encoding='utf-8'))
        sampled = {venue['venue_id']: venue for venue in data['venues']}
        # Then two papers per initial venue do not silently cover other venues.
        self.assertEqual(len(data['papers']), 4)
        for venue in ('ISCA', 'CAL'):
            self.assertEqual(sampled[venue]['sample_size'], 2)
            self.assertIn('no representative sample', sampled[venue]['scope_limit'])
        for venue in ('MICRO', 'HPCA', 'ASPLOS', 'SOSP', 'OSDI'):
            self.assertEqual(sampled[venue]['sampling_status'], 'unsampled')
            self.assertEqual(sampled[venue]['paper_ids'], [])
            self.assertEqual(sampled[venue]['sample_size'], 0)
        for observation in data['observations']:
            self.assertEqual(observation['category'], 'observed_pattern')
            self.assertEqual(observation['generalization'], 'sample_only')
            self.assertIn('not a venue-wide norm', observation['scope_limit'])

    def test_profile_compatibility_when_observations_link_sampled_papers(self) -> None:
        # Given the two existing official profiles with additive style observations.
        for filename in ('isca-2026-research-submission.json', 'cal-continuing-letter-submission.json'):
            # When reading the legacy schema fields.
            profile = json.loads((SKILL / 'venues/profiles' / filename).read_text(encoding='utf-8'))
            # Then only the exact three-field observation shape is exposed there.
            self.assertEqual(profile['schema_version'], 1)
            self.assertEqual(len(profile['writing_style_observations']), 2)
            for observation in profile['writing_style_observations']:
                self.assertEqual(set(observation), {'paper_url', 'observation', 'scope_limit'})
                self.assertIn('PDF p', observation['observation'])


if __name__ == '__main__':
    unittest.main()
