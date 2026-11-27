"""init-env leaves the Nextcloud data alone and only fixes wrong owners (pipeline unattended-pipeline/250).

init-env runs first on every boot. It used to `chown -R www-data` /data/nextcloud and a hard-coded
/share/nextcloud: that changed the owner of a customer's /share/nextcloud even when
NEXTCLOUD_DATADIR points elsewhere (seen on an N2840: 1000:1000 -> 33:33), and it took longer the
more files there were. init-nextcloud-config already fixes the owners of /data/nextcloud and the
configured data directory (only entries with another owner), so init-env no longer does.
PostgreSQL and Redis data: only entries that are not owned by postgres/redis are changed, so a
restore with wrong owners is still fixed and nothing is written otherwise.

The real script runs with stubbed commands in a temp directory.
"""
import grp
import os
import pwd
import subprocess
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SCRIPT = BASE / 'rootfs/etc/s6-overlay/s6-rc.d/init-env/run'
ME = pwd.getpwuid(os.getuid()).pw_name
MY_GROUP = grp.getgrgid(os.getgid()).gr_name


class InitEnv(unittest.TestCase):
    def run_env(self, owner, datadir='/share/nextcloud'):
        """Run init-env; owner:owner stands in for postgres:postgres and redis:redis."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bindir = root / 'bin'
            bindir.mkdir()
            stubs = {
                # woow-options KEY DEFAULT: the data directory option, everything else its default.
                'woow-options': f'if [ "$1" = NEXTCLOUD_DATADIR ]; then echo "{datadir}"; else echo "$2"; fi',
                'openssl': 'echo generated',
                'chown': 'printf "chown %s\\n" "$*" >> "$CALL_LOG"',
                'chmod': 'printf "chmod %s\\n" "$*" >> "$CALL_LOG"',
            }
            for name, body in stubs.items():
                p = bindir / name
                p.write_text(f'#!/bin/sh\n{body}\nexit 0\n')
                p.chmod(0o700)
            for d in ['run/postgresql', 'run/redis', 'data/postgres/base', 'data/redis']:
                (root / d).mkdir(parents=True)
            (root / 'data/postgres/base/1').write_text('')
            (root / 'data/redis/dump.rdb').write_text('')
            text = SCRIPT.read_text()
            for prefix in ['/data', '/run', '/share']:
                text = text.replace(prefix, str(root) + prefix)
            text = text.replace('#!/command/with-contenv bash', '#!/bin/bash')
            for user in ['postgres', 'redis']:
                text = text.replace(f'{user}:{user}', f'{owner}:{owner}')
                text = text.replace(f'-user {user}', f'-user {owner}').replace(f'-group {user}', f'-group {owner}')
            (root / 'init.sh').write_text(text)
            log = root / 'calls'
            env = dict(os.environ, PATH=f'{bindir}:/usr/bin:/bin', CALL_LOG=str(log))
            result = subprocess.run(['/bin/bash', str(root / 'init.sh')], env=env,
                                    capture_output=True, text=True, timeout=20)
            calls = log.read_text().splitlines() if log.exists() else []
            share_created = (root / 'share/nextcloud').exists()
            return result, [c.replace(str(root), '') for c in calls], share_created

    def test_nextcloud_data_is_not_chowned(self):
        result, calls, _ = self.run_env('root')
        self.assertEqual(result.returncode, 0, result.stderr)
        for c in calls:
            self.assertNotIn('/share/nextcloud', c)
            self.assertNotIn('/data/nextcloud', c)
            self.assertNotIn('www-data', c)

    def test_share_nextcloud_is_not_created_when_the_data_directory_is_elsewhere(self):
        result, _, share_created = self.run_env('root', datadir='/share/other')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(share_created)

    def test_nothing_is_chowned_when_owners_are_already_right(self):
        if ME != MY_GROUP:
            self.skipTest('needs a user whose primary group has the same name')
        result, calls, _ = self.run_env(ME)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([c for c in calls if c.startswith('chown')], [])
        self.assertIn('chmod 700 /data/postgres', calls)

    def test_wrong_owners_are_still_fixed(self):
        result, calls, _ = self.run_env('root')
        self.assertEqual(result.returncode, 0, result.stderr)
        chowned = ' '.join(c for c in calls if c.startswith('chown'))
        self.assertNotIn('chown -R', chowned)
        self.assertIn('chown -h root:root', chowned)
        for path in ['/data/postgres/base/1', '/run/postgresql', '/data/redis/dump.rdb', '/run/redis']:
            self.assertIn(path, chowned)
        self.assertIn('chmod 700 /data/postgres', calls)


if __name__ == '__main__':
    unittest.main()
