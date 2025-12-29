"""Registry for descriptor configuration profiles."""

from __future__ import annotations

import copy
from dataclasses import replace
from typing import Optional

from pretty_little_summary.descriptor_utils import DescribeConfig


class DescribeConfigRegistry:
    """
    Registry for DescribeConfig profiles.

    Allows callers to register named profiles and switch defaults.
    """

    _profiles: dict[str, DescribeConfig] = {"default": DescribeConfig()}
    _default_name: str = "default"

    @classmethod
    def register(cls, name: str, config: DescribeConfig, set_default: bool = False) -> None:
        cls._profiles[name] = config
        if set_default:
            cls._default_name = name

    @classmethod
    def get(cls, name: Optional[str] = None) -> DescribeConfig:
        profile_name = name or cls._default_name
        config = cls._profiles.get(profile_name, cls._profiles["default"])
        return copy.deepcopy(config)

    @classmethod
    def set_default(cls, name: str) -> None:
        if name in cls._profiles:
            cls._default_name = name
        else:
            cls._profiles[name] = DescribeConfig()
            cls._default_name = name

    @classmethod
    def list_profiles(cls) -> list[str]:
        return sorted(cls._profiles.keys())

    @classmethod
    def update(cls, name: str, **kwargs) -> DescribeConfig:
        config = cls._profiles.get(name, DescribeConfig())
        updated = replace(config, **kwargs)
        cls._profiles[name] = updated
        return copy.deepcopy(updated)
