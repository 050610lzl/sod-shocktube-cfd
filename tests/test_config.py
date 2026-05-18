"""
配置加载与验证测试 (tests/test_config.py)
=========================================
验证 YAML/JSON 配置文件加载、自动格式检测、参数验证。

依据: Build文档 §3.1, §7.1
"""

import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from run_simulation import (
    load_config, load_json_config, load_any_config, validate_config,
    REQUIRED_CONFIG_KEYS
)


SAMPLE_YAML_STR = """\
mesh:
  n_points: 100
  x_left: 0.0
  x_right: 1.0
physics:
  gamma: 1.4
  diaphragm_pos: 0.5
  left_state:
    rho: 1.0
    u: 0.0
    p: 1.0
  right_state:
    rho: 0.125
    u: 0.0
    p: 0.1
simulation:
  t_final: 0.2
  cfl: 0.8
  boundary_type: zero_gradient
schemes:
  - lax_friedrichs
  - upwind
output:
  data_dir: results/data
  exact_dir: results/exact
  figures_dir: results/figures
  error_report: results/error_report.csv
"""

SAMPLE_JSON_DICT = {
    "mesh": {"n_points": 100, "x_left": 0.0, "x_right": 1.0},
    "physics": {
        "gamma": 1.4, "diaphragm_pos": 0.5,
        "left_state": {"rho": 1.0, "u": 0.0, "p": 1.0},
        "right_state": {"rho": 0.125, "u": 0.0, "p": 0.1}
    },
    "simulation": {"t_final": 0.2, "cfl": 0.8, "boundary_type": "zero_gradient"},
    "schemes": ["lax_friedrichs", "upwind"],
    "output": {
        "data_dir": "results/data", "exact_dir": "results/exact",
        "figures_dir": "results/figures", "error_report": "results/error_report.csv"
    }
}


def _write_temp_file(ext, content):
    tmp = tempfile.NamedTemporaryFile(suffix=ext, mode='w', encoding='utf-8',
                                       delete=False)
    tmp.write(content)
    tmp.close()
    return tmp.name


def test_load_yaml_config():
    path = _write_temp_file('.yaml', SAMPLE_YAML_STR)
    try:
        cfg = load_config(path)
        assert cfg['mesh']['n_points'] == 100
        assert cfg['physics']['left_state']['rho'] == 1.0
    finally:
        os.unlink(path)


def test_load_json_config():
    path = _write_temp_file('.json', json.dumps(SAMPLE_JSON_DICT, indent=2))
    try:
        cfg = load_json_config(path)
        assert cfg['mesh']['n_points'] == 100
        assert cfg['physics']['left_state']['rho'] == 1.0
    finally:
        os.unlink(path)


def test_load_any_config_yaml():
    path = _write_temp_file('.yaml', SAMPLE_YAML_STR)
    try:
        cfg = load_any_config(path)
        assert cfg is not None
    finally:
        os.unlink(path)


def test_load_any_config_json():
    path = _write_temp_file('.json', json.dumps(SAMPLE_JSON_DICT, indent=2))
    try:
        cfg = load_any_config(path)
        assert cfg is not None
    finally:
        os.unlink(path)


def test_load_any_config_yml():
    path = _write_temp_file('.yml', SAMPLE_YAML_STR)
    try:
        cfg = load_any_config(path)
        assert cfg is not None
    finally:
        os.unlink(path)


def test_load_any_config_unsupported():
    path = _write_temp_file('.txt', "hello")
    try:
        with pytest.raises(ValueError, match="不支持的配置文件格式"):
            load_any_config(path)
    finally:
        os.unlink(path)


def test_validate_config_valid():
    validate_config(SAMPLE_JSON_DICT, 'test.json')


def test_validate_config_missing_key():
    bad = dict(SAMPLE_JSON_DICT)
    del bad['mesh']
    with pytest.raises(ValueError, match="缺少必需配置节"):
        validate_config(bad, 'test.json')


def test_validate_config_invalid_cfl():
    bad = dict(SAMPLE_JSON_DICT)
    bad['simulation'] = dict(bad['simulation'])
    bad['simulation']['cfl'] = 5.0
    with pytest.raises(ValueError, match="cfl"):
        validate_config(bad, 'test.json')


def test_validate_config_invalid_boundary():
    bad = dict(SAMPLE_JSON_DICT)
    bad['simulation'] = dict(bad['simulation'])
    bad['simulation']['boundary_type'] = 'nonexistent'
    with pytest.raises(ValueError, match="boundary_type"):
        validate_config(bad, 'test.json')


def test_validate_config_invalid_scheme():
    bad = dict(SAMPLE_JSON_DICT)
    bad['schemes'] = ['unknown_scheme']
    with pytest.raises(ValueError, match="未知格式"):
        validate_config(bad, 'test.json')


def test_validate_config_empty_schemes():
    bad = dict(SAMPLE_JSON_DICT)
    bad['schemes'] = []
    with pytest.raises(ValueError, match="非空列表"):
        validate_config(bad, 'test.json')


def test_validate_config_invalid_gamma():
    bad = dict(SAMPLE_JSON_DICT)
    bad['physics'] = dict(bad['physics'])
    bad['physics']['gamma'] = 0.05
    with pytest.raises(ValueError, match="gamma"):
        validate_config(bad, 'test.json')


def test_validate_config_invalid_n_points():
    bad = dict(SAMPLE_JSON_DICT)
    bad['mesh'] = dict(bad['mesh'])
    bad['mesh']['n_points'] = 5
    with pytest.raises(ValueError, match="n_points"):
        validate_config(bad, 'test.json')


def test_validate_config_invalid_t_final():
    bad = dict(SAMPLE_JSON_DICT)
    bad['simulation'] = dict(bad['simulation'])
    bad['simulation']['t_final'] = 0.0001
    with pytest.raises(ValueError, match="t_final"):
        validate_config(bad, 'test.json')


def test_yaml_json_equivalent():
    yaml_cfg = load_config('config/simulation_config.yaml')
    json_cfg = load_json_config('config/simulation_config.json')
    assert yaml_cfg['mesh'] == json_cfg['mesh']
    assert yaml_cfg['physics']['left_state'] == json_cfg['physics']['left_state']
    assert yaml_cfg['simulation'] == json_cfg['simulation']
    assert yaml_cfg['schemes'] == json_cfg['schemes']
    assert yaml_cfg['output'] == json_cfg['output']


def test_custom_json_config_loads():
    cfg = load_json_config('config/simulation_config_custom_sod.json')
    assert cfg['physics']['left_state']['p'] == 10.0
    assert cfg['simulation']['boundary_type'] == 'transmissive'
    assert cfg['simulation']['cfl'] == 0.5
    assert 'godunov' in cfg['schemes']


def test_high_res_json_config_loads():
    cfg = load_json_config('config/simulation_config_high_res.json')
    assert cfg['mesh']['n_points'] == 800
    assert len(cfg['schemes']) == 3
    assert cfg['output']['error_report'] == 'results/error_report_hires.csv'