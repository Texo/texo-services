package tags

type TagCollection struct {
	Tags []Tag `json:"tags"`
}

/*
Creates a new TagCollection
*/
func NewTagCollection() TagCollection {
	return TagCollection{
		Tags: make([]Tag, 0),
	}
}
