package posts

type PostCollection struct {
	CurrentPage  int    `json:"currentPage"`
	LastPage     int    `json:"lastPage"`
	NextPage     int    `json:"nextPage"`
	NumPages     int    `json:"numPages"`
	NumPosts     int    `json:"numPosts"`
	Posts        []Post `json:"posts"`
	PreviousPage int    `json:"previousPage"`
}

/*
Creates a new PostCollection
*/
func NewPostCollection() PostCollection {
	return PostCollection{
		CurrentPage:  0,
		LastPage:     0,
		NextPage:     0,
		NumPages:     0,
		NumPosts:     0,
		Posts:        make([]Post, 0),
		PreviousPage: 0,
	}
}
