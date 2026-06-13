import src.app as app_module


def test_get_activities_returns_all_activities_and_required_fields(client):
    # Arrange
    required_fields = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == len(app_module.activities)

    for activity_name, details in data.items():
        assert activity_name in app_module.activities
        assert required_fields.issubset(details.keys())
        assert isinstance(details["participants"], list)


def test_post_signup_with_valid_activity_and_email_returns_success(client):
    # Arrange
    activity_name = "Chess Club"
    new_email = "new.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}
    assert new_email in app_module.activities[activity_name]["participants"]


def test_post_signup_with_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_post_signup_with_duplicate_email_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = app_module.activities[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_post_signup_successfully_increments_participant_count(client):
    # Arrange
    activity_name = "Science Club"
    email = "count.check@mergington.edu"
    starting_count = len(app_module.activities[activity_name]["participants"])

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    ending_count = len(app_module.activities[activity_name]["participants"])
    assert ending_count == starting_count + 1


def test_delete_participant_with_valid_activity_and_email_returns_success(client):
    # Arrange
    activity_name = "Art Club"
    email_to_remove = app_module.activities[activity_name]["participants"][0]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": email_to_remove}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email_to_remove} from {activity_name}"}
    assert email_to_remove not in app_module.activities[activity_name]["participants"]


def test_delete_participant_with_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_participant_with_missing_email_returns_404(client):
    # Arrange
    activity_name = "Basketball"
    missing_email = "missing@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": missing_email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_delete_participant_successfully_decrements_participant_count(client):
    # Arrange
    activity_name = "Debate Team"
    email_to_remove = app_module.activities[activity_name]["participants"][0]
    starting_count = len(app_module.activities[activity_name]["participants"])

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": email_to_remove}
    )

    # Assert
    assert response.status_code == 200
    ending_count = len(app_module.activities[activity_name]["participants"])
    assert ending_count == starting_count - 1


def test_state_isolation_after_mutation_restores_original_data(client):
    # Arrange
    activity_name = "Tennis"
    email = "isolated@mergington.edu"
    assert email not in app_module.activities[activity_name]["participants"]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in app_module.activities[activity_name]["participants"]


def test_state_isolation_followup_starts_from_clean_state(client):
    # Arrange
    activity_name = "Tennis"
    email = "isolated@mergington.edu"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert email not in app_module.activities[activity_name]["participants"]
