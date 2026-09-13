"""Execute the vendored header resolver, including hostile ambient navigation."""
from pathlib import Path
import shutil
import subprocess


def test_title_uses_only_declared_parent():
    root = Path(__file__).resolve().parents[1]
    node = shutil.which('node')
    assert node, 'Node is required for executable header navigation coverage'
    script = r'''
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const source = fs.readFileSync('templates/shell_v2/nikas-specialized-shell.js', 'utf8');
const forbidden = () => { throw new Error('ambient navigation must not be read'); };
const context = { URL, URLSearchParams, window: { location: {
 origin: 'http://ha.test', pathname: '/dashboard-device/details',
 get search() { return '?return_to=/dashboard-actions/home&from=/dashboard-house-v13/home'; }
}, localStorage: {getItem:forbidden,setItem:forbidden}, sessionStorage:{getItem:forbidden,removeItem:forbidden}}, document:{get referrer(){return 'http://ha.test/dashboard-infrastructure/overview';}} };
vm.runInNewContext(source + '\nthis.resolve = captureNikasShellReturnRoute;', context);
for (const parent of ['/home/overview', '/dashboard-device']) {
 assert.equal(context.resolve({panelId:'test',parentRoute:parent,safeReturnRoute:'/dashboard-actions/home'}), parent);
}
for (const parent of [undefined, '', '//evil.test/path', 'https://evil.test/path', 'javascript:alert(1)', 'house.devices', '/dashboard-device/details']) {
 assert.equal(context.resolve({panelId:'test',parentRoute:parent,safeReturnRoute:'/dashboard-actions/home'}), '/home/overview');
}
'''
    result = subprocess.run([node, '-e', script], cwd=root, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
