package posts

import (
	"fmt"
)

type Post struct {
	Id                int    `json:"id"`
	Title             string `json:"title"`
	AuthorId          int    `json:"authorId"`
	Author            string `json:"author"`
	Slug              string `json:"slug"`
	Content           string `json:"content"`
	RenderedContent   string `json:"renderedContent"`
	CreatedDateTime   string `json:"createdDateTime"`
	PublishedDateTime string `json:"publishedDateTime"`
	PublishedYear     int    `json:"publishedYear"`
	PublishedMonth    int    `json:"publishedMonth"`
	PostStatusId      int    `json:"postStatusId"`
	Status            string `json:"status"`
	TagList           string `json:"tagList"`
	TagIdList         string `json:"tagIdList"`
}

func (this *Post) PermaLink() string {
	return fmt.Sprintf("/post/%d/%d/%s", this.PublishedYear, this.PublishedMonth, this.Slug)
}
