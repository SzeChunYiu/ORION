from __future__ import annotations

import sys
import time
from pathlib import Path

import pytest

import orion_research_harness.local_tools as local_tools
from orion_research_harness.workspace import ResearchWorkspace


def test_file_list_fails_closed_when_directory_exceeds_bound(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project=tmp_path/'project';project.mkdir()
    for index in range(4):(project/f'f{index}.txt').write_text('x')
    workspace=ResearchWorkspace.initialize(project/'ws',project_root=project)
    monkeypatch.setattr(local_tools,'_MAX_LIST_ENTRIES',3)
    with pytest.raises(OverflowError,match='narrow the listing scope'):
        local_tools.execute_local(workspace,'FILE_LIST',{'path':'.'})


def test_process_timeout_defaults_to_120_and_explicit_qg3_override_is_bounded(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv('ORION_HARNESS_MAX_PROCESS_TIMEOUT_SECONDS',raising=False)
    assert local_tools._validated_process_timeout(300)==120
    monkeypatch.setenv('ORION_HARNESS_MAX_PROCESS_TIMEOUT_SECONDS','600')
    assert local_tools._validated_process_timeout(600)==600
    assert local_tools._validated_process_timeout(9999)==600
    monkeypatch.setenv('ORION_HARNESS_MAX_PROCESS_TIMEOUT_SECONDS','601')
    with pytest.raises(ValueError,match='must be between 1 and 600'):
        local_tools._validated_process_timeout(60)


def test_descendant_holding_output_pipe_cannot_hang_completed_process(tmp_path: Path):
    project=tmp_path/'project';project.mkdir();workspace=ResearchWorkspace.initialize(project/'ws',project_root=project,allow_process_tools=True)
    code="import subprocess,sys; subprocess.Popen([sys.executable,'-c','import time; time.sleep(10)']); print('parent-complete')"
    started=time.monotonic();result=local_tools.execute_local(workspace,'PYTHON',{'code':code,'timeout':5});elapsed=time.monotonic()-started
    assert result['returncode']==0 and 'parent-complete' in result['stdout'] and elapsed<5


def test_shell_uses_argv_without_shell_interpolation(tmp_path: Path):
    project=tmp_path/'project';project.mkdir();workspace=ResearchWorkspace.initialize(project/'ws',project_root=project,allow_process_tools=True)
    result=local_tools.execute_local(workspace,'SHELL',{'argv':[sys.executable,'-c','import sys; print(sys.argv[1])','$(echo injected)']})
    assert result['returncode']==0 and result['stdout'].strip()=='$(echo injected)'
