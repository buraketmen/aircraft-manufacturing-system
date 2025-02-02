from dataclasses import dataclass

@dataclass(frozen=True)
class TeamTypes:
    ADMIN: str = "ADMIN"
    WING: str = 'WING'
    BODY: str = 'BODY'
    TAIL: str = 'TAIL'
    AVIONICS: str = 'AVIONICS'
    ASSEMBLY: str = 'ASSEMBLY'

DEFAULT_TEAM_USERS =  {
    TeamTypes.ADMIN: [
        ('admin', 'Burak', 'Ketmen', 'admin'),
    ],
    TeamTypes.WING: [
        ('wing-1', 'Ahmet', 'Yılmaz', '123456'),
        ('wing-2', 'Mehmet', 'Demir', '123456'),
    ],
    TeamTypes.TAIL: [
        ('tail-1', 'Ayşe', 'Kaya', '123456'),
        ('tail-2', 'Fatma', 'Çelik', '123456'),
    ],
    TeamTypes.BODY: [
        ('body-1', 'Mustafa', 'Yıldız', '123456'),
        ('body-2', 'Ali', 'Şahin', '123456'),
    ],
    TeamTypes.AVIONICS: [
        ('avionics-1', 'Zeynep', 'Arslan', '123456'),
        ('avionics-2', 'Elif', 'Öztürk', '123456'),
    ],
    TeamTypes.ASSEMBLY: [
        ('assembly-1', 'Can', 'Koç', '123456'),
        ('assembly-2', 'Mert', 'Aydın', '123456'),
    ],
}