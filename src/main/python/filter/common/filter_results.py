from typing import Optional, Dict, Any

from pydantic import BaseModel


class FilterResults(BaseModel):
	# Custom classes inside attributes field are forbidden to allow simple serialization/deserialization inside AnnotationModel.
	# For the same reason subclassing FilterResults is forbidden.
	text: Optional[str]
	attributes: Optional[Dict[str, Any]]

	def __init__(self, text: Optional[str], attributes: Optional[Dict[str, Any]]):
		super().__init__(text=text, attributes=attributes)