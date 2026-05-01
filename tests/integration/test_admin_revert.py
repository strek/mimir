"""S09–S10 admin revert skeleton."""

from methodology.versioning.pit_skeletons import (
    scenario_s09_admin_revert_draft,
    scenario_s10_post_revert_edit_release,
)


def test_revert_keeps_version_changes_status_skeleton():
    scenario_s09_admin_revert_draft()


def test_post_revert_edits_then_release_skeleton():
    scenario_s10_post_revert_edit_release()
