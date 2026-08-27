"""Google OAuth authorization pipeline step.

@file authenticate_with_google_step.py
@brief Authorizes the local pipeline to act as a selected Google user.
"""

from google_drive import GoogleDriveOAuthCredentials
from pipeline.pipeline_context import PipelineContext
from utils import LOGGER


class AuthenticateWithGoogleStep:
    """Pipeline step that creates or refreshes the local Google OAuth token."""

    name = "auth-with-google"

    def run(self, pipeline_context: PipelineContext):
        """Authorize the pipeline without generating reports or modifying Drive.

        @param pipeline_context Shared pipeline state.
        """
        GoogleDriveOAuthCredentials().authorize()
        LOGGER.info("Google authorization completed")
