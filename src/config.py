from dataclasses import dataclass

@dataclass
class StudyArea:
    latitude: float
    longitude: float
    radius: int

study_area = StudyArea(
    latitude=-23.675394,
    longitude=-46.788774,
    radius=2500
)