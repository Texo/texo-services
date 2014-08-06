package posts

type PostCollection struct {
	Posts []Post `json:"posts"`
}

/*
Creates a new PostCollection
*/
func NewPostCollection() PostCollection {
	return PostCollection{
		Posts: make([]Post, 0),
	}
}