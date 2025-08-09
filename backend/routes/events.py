from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, session
from sqlalchemy import exists
from database import get_events_db
from schemas import EventsSchema
from models.events import Event
from datetime import datetime
from responces import EventsResponse
from typing import List


router = APIRouter()

MONTHS = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}

def parser_day(day_string):
    return "".join(ch for ch in day_string if ch.isdigit())

@router.get("/{event_id}")
async def get_event(event_id: int, db: Session = Depends(get_events_db)):
    return db.query(Event).filter(Event.id == event_id).first()


@router.post("/create_events")
async def create_event(event: EventsSchema, db: Session = Depends(get_events_db)):
    date =  event.date
    print(event.event_name)
    temp_date = date.split("-")

    month = 0
    day = 0
    if temp_date != '':
        start_date = ""
        end_date = ""
        
        if len(temp_date) == 1:
            start_date = end_date = temp_date[0].strip()
        elif len(temp_date) == 2:
            start_date = temp_date[0].strip()
            end_date = temp_date[1].strip()
        else:
            raise HTTPException(status_code=422, detail="Invalid date format")
        
        start_month = MONTHS[start_date[:3]]
        end_month = MONTHS[end_date[:3]]
        start_day = parser_day(start_date)
        end_day = parser_day(end_date)
        full_start = f"{start_month}-{start_day}-2025"
        full_end = f"{end_month}-{end_day}-2025"
        date_start = datetime.strptime(full_start, "%m-%d-%Y")
        date_end = datetime.strptime(full_end, "%m-%d-%Y")
        print(date_start, date_end)
        link_string = str(event.link)

    try:
        # Check if the event already exists
        event_exists = db.query(
            exists().where(Event.event_name == event.event_name)
        ).scalar()

        if event_exists:
            return {"status": 409, "message": "Record Already Exists"}
        else:
            # Create a new Event instance
            new_event = Event(
                event_name=event.event_name,
                location=event.location,
                start_date=date_start,
                end_date=date_end,
                prize=event.prize,
                link=link_string,
                event_id=event.id,
            )

            db.add(new_event)
            db.commit()
            return {"status": 201, "message": "Event Created Successfully"}

    except SQLAlchemyError as e:
        db.rollback()
        return {"status": 500, "message": f"An error occurred while processing your request. {e}"}

@router.get("/get_links/", response_model=List[EventsResponse])
async def get_links(db: Session = Depends(get_events_db)):
    try:
        links = db.query(Event.link).all()
        formatted_links = [{"link": link[0]} for link in links]
        return formatted_links
    except Exception as e:
        # Log the exception (use a logging framework in production)
        print(f"Error retrieving links: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving links."
        )


@router.get("/")
async def root():
    return {"Hello": "World"}