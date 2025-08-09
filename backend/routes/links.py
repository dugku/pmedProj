import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import exists
from database import get_links_db
from models.links import Links
from schemas import LinksSchema
from typing import List
from responces import LinksResponse

router = APIRouter()


@router.post("/create_links")
async def create_links(links: LinksSchema, db: Session = Depends(get_links_db)):

    match_id = links.demo_url.split("/")[4]

    try:
        link_exists = db.query(
            exists().where(Links.match_id == match_id)
        ).scalar()

        if link_exists:
            return {"status": 409, "message": "Record Already Exists"}
        else:
            link = Links(
                demo_url=links.demo_url,
                match_id=match_id,
            )
            db.add(link)
            db.commit()
            return {"status": 201, "message": "Match Created Successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        return {"status": 500, "message": "An error occurred while processing your request."}

@router.get("/get_match_links/", response_model=List[LinksResponse])
async def get_match_links(db: Session = Depends(get_links_db)):
    try:
        matches = db.query(Links.match_id, Links.demo_url).filter(Links.parsed == False).limit(225).all()

        formatted_matches = [
            {"match_id": match.match_id, "demo_url": match.demo_url} for match in matches
        ]
        #logging.info(f"{formatted_matches}")
        return formatted_matches
    except Exception as e:

        print(f"Error retrieving links: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving links."
        )

@router.get("/{id_match}")
async def update_parsed(id_match: str, db: Session = Depends(get_links_db)):
    match = db.query(Links).filter(Links.match_id == id_match).first()

    if match:
        match.parsed = True
        db.commit()
    return {"status": 200, "message": "Match Updated Successfully"}