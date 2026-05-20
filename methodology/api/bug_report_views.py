"""REST endpoint for bug reports (MCP HTTP facade)."""

from __future__ import annotations

import logging

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from methodology.services.bug_report_service import BugReportService

logger = logging.getLogger(__name__)


class BugReportSubmitView(APIView):
    """
    POST JSON bug report; same backend as the web feedback widget.

    Permission: authenticated API user (session or DRF token).
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        description = (request.data.get("description") or "").strip()
        page_context = (request.data.get("page_context") or "").strip()
        posted_email = (request.data.get("reporter_email") or "").strip()
        reporter_email = posted_email or (
            getattr(request.user, "email", None) or ""
        ).strip()

        logger.info(
            "BugReportSubmitView POST user_id=%s desc_len=%s has_page_context=%s",
            getattr(request.user, "pk", None),
            len(description),
            bool(page_context),
        )

        try:
            result = BugReportService.submit_bug(
                description,
                reporter_email,
                source="mcp",
                page_context=page_context,
            )
        except ValueError as e:
            logger.warning("BugReportSubmitView rejected: %s", e)
            return Response({"detail": str(e)}, status=400)

        return Response(result, status=201)
