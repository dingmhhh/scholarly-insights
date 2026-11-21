
import firebase_admin


def get_firebase_app():
    """
    Initialize Firebase Admin SDK once.
    """
    try:
        return firebase_admin.get_app()
    except ValueError:
        return firebase_admin.initialize_app(
            options={
                "projectId": "scholarly-insights-2aac8"
            }
        )
