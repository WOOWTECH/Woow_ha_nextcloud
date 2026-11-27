"""coolwsd stops within Supervisor's 10 s even while it is still starting (pipeline unattended-pipeline/250).

Supervisor SIGKILLs the add-on 10 s after its SIGTERM (exit 137). coolwsd that is told to stop
while it is still starting does not look at the request until its startup reaches a certain
point: about 5.6 s on an N2840, on top of the rest of the stop. svc-coolwsd therefore runs
coolwsd under woow-coolwsd-run, which handles s6's SIGTERM:

- coolwsd not ready yet (discovery does not answer): SIGKILL coolwsd and its child processes.
  No document can be open yet, so nothing is lost.
- coolwsd ready: forward SIGTERM, so open documents are saved and closed as before.

coolwsd exiting on its own makes the wrapper exit with the same code, so s6 still sees the
service go down and restarts it. The tests run the real wrapper with a stub coolwsd and curl.
"""
import os
import signal
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
WRAPPER = BASE / 'rootfs/usr/local/bin/woow-coolwsd-run'
RUN = BASE / 'rootfs/etc/s6-overlay/s6-rc.d/svc-coolwsd/run'

# Stand-in for coolwsd: records SIGTERM, starts a child process (forkit/kit), then waits.
STUB_COOLWSD = r'''#!/bin/bash
trap 'echo term >> "$DIR/events"; kill $(cat "$DIR/grandchild"); exit 0' TERM
sleep 300 >/dev/null 2>&1 &
echo $! > "$DIR/grandchild"
echo $$ > "$DIR/child"
if [[ -n "${EXIT_WITH:-}" ]]; then exit "$EXIT_WITH"; fi
while :; do wait; done
'''


def alive(pid):
    """True while pid exists and is not a zombie."""
    try:
        state = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[0]
    except (FileNotFoundError, ProcessLookupError):
        return False
    return state != 'Z'


class Wrapper(unittest.TestCase):
    def start(self, ready, exit_with=None):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        d = Path(tmp.name)
        bindir = d / 'bin'
        bindir.mkdir()
        (bindir / 'coolwsd').write_text(STUB_COOLWSD)
        # The readiness probe; exit 7 = connection refused, as while coolwsd is still starting.
        (bindir / 'curl').write_text(f'#!/bin/sh\necho "curl $*" >> "$DIR/events"\nexit {0 if ready else 7}\n')
        for p in bindir.iterdir():
            p.chmod(0o700)
        env = dict(os.environ, PATH=f'{bindir}:/usr/bin:/bin', DIR=str(d))
        if exit_with is not None:
            env['EXIT_WITH'] = str(exit_with)
        proc = subprocess.Popen(['/bin/bash', str(WRAPPER), 'coolwsd', '--o:x=1'], env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self.addCleanup(lambda: proc.poll() is None and proc.kill())
        if exit_with is None:
            deadline = time.monotonic() + 10
            while not (d / 'child').exists() and time.monotonic() < deadline:
                time.sleep(0.05)
            self.assertTrue((d / 'child').exists(), 'stub coolwsd did not start')
            time.sleep(0.2)  # let the wrapper reach its wait
        return proc, d

    def pids(self, d):
        child, grandchild = int((d / 'child').read_text()), int((d / 'grandchild').read_text())
        self.addCleanup(lambda: [os.kill(p, signal.SIGKILL) for p in (child, grandchild) if alive(p)])
        return child, grandchild

    def events(self, d):
        f = d / 'events'
        return f.read_text().splitlines() if f.exists() else []

    def test_term_while_starting_kills_coolwsd_and_its_children(self):
        proc, d = self.start(ready=False)
        child, grandchild = self.pids(d)
        t0 = time.monotonic()
        proc.send_signal(signal.SIGTERM)
        out, _ = proc.communicate(timeout=10)
        self.assertLess(time.monotonic() - t0, 3)
        self.assertEqual(proc.returncode, 128 + signal.SIGKILL, out)
        self.assertNotIn('term', self.events(d), 'coolwsd got SIGTERM instead of SIGKILL')
        deadline = time.monotonic() + 3
        while (alive(child) or alive(grandchild)) and time.monotonic() < deadline:
            time.sleep(0.05)
        self.assertFalse(alive(child), 'coolwsd still running')
        self.assertFalse(alive(grandchild), 'a coolwsd child process is still running')
        self.assertIn('still starting', out)
        self.assertNotIn('ERROR', out)

    def test_term_when_ready_forwards_term(self):
        proc, d = self.start(ready=True)
        child, grandchild = self.pids(d)
        proc.send_signal(signal.SIGTERM)
        out, _ = proc.communicate(timeout=10)
        self.assertEqual(proc.returncode, 0, out)
        events = self.events(d)
        self.assertEqual(events[-1], 'term', events)
        self.assertTrue(any('/hosting/discovery' in e for e in events), events)
        self.assertFalse(alive(child))
        self.assertNotIn('ERROR', out)

    def test_exit_code_of_coolwsd_is_passed_on(self):
        proc, _ = self.start(ready=True, exit_with=3)
        proc.communicate(timeout=10)
        self.assertEqual(proc.returncode, 3)

    def test_coolwsd_killed_from_outside_is_reported_as_such(self):
        # coolwsd crashing (here: SIGKILL from elsewhere) makes the service go down, so s6 restarts it.
        proc, d = self.start(ready=True)
        child, _ = self.pids(d)
        os.kill(child, signal.SIGKILL)
        proc.communicate(timeout=10)
        self.assertEqual(proc.returncode, 128 + signal.SIGKILL)


class RunScript(unittest.TestCase):
    def test_svc_coolwsd_runs_coolwsd_under_the_wrapper(self):
        text = RUN.read_text()
        self.assertIn('exec woow-coolwsd-run gosu cool /usr/bin/coolwsd', text)
        self.assertNotIn('exec gosu cool /usr/bin/coolwsd', text)
        self.assertIn('exec sleep infinity', text)  # Collabora disabled: unchanged

    def test_service_type_and_dependencies_are_unchanged(self):
        svc = RUN.parent
        self.assertEqual((svc / 'type').read_text().strip(), 'longrun')
        self.assertEqual(sorted(p.name for p in (svc / 'dependencies.d').iterdir()), ['init-collabora-config'])


if __name__ == '__main__':
    unittest.main()
