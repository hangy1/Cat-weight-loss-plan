"""SQLAlchemy database models"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Product(Base):
    """Pet food product model"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(Text, unique=True, nullable=False, index=True)
    brand = Column(Text, nullable=True)
    name = Column(Text, nullable=False)
    food_type = Column(Text, nullable=False)  # 'dry' or 'wet'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to nutrition sources
    nutrition_sources = relationship("NutritionSource", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product(id={self.id}, external_id='{self.external_id}', name='{self.name}')>"


class NutritionSource(Base):
    """Nutrition data from various sources"""
    __tablename__ = "nutrition_sources"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)

    source = Column(Text, nullable=False)  # manufacturer | chewy | petco | petsmart | openfoodfacts

    # Calorie measurements in different units
    kcal_per_100g = Column(Float, nullable=True)
    kcal_per_kg = Column(Float, nullable=True)
    kcal_per_oz = Column(Float, nullable=True)
    kcal_per_cup = Column(Float, nullable=True)
    kcal_per_can = Column(Float, nullable=True)

    # Serving size information
    grams_per_cup = Column(Float, nullable=True)
    serving_size_oz = Column(Float, nullable=True)

    # Data quality
    confidence = Column(Float, nullable=True)  # 0.0 - 1.0

    # Debug/tracing
    raw_text = Column(Text, nullable=True)

    scraped_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to product
    product = relationship("Product", back_populates="nutrition_sources")

    def __repr__(self):
        return f"<NutritionSource(id={self.id}, product_id={self.product_id}, source='{self.source}')>"
