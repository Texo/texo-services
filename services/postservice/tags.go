package postservice

import (
	"fmt"

	"github.com/texo/texo-services/database"
	"github.com/texo/texo-services/model/tags"
)

/*
Creates a link to blog posts filtered by a specific tag.
*/
func CreateLinkToPostsByTag(tag string) string {
	return fmt.Sprintf("/posts/1/tag/%s", tag)
}

/*
Queries the database for a specific tag by ID.
*/
func GetTag(id int) (tags.Tag, error) {
	var err error
	var result tags.Tag

	rows, err := database.Db.Query(`
		SELECT
			posttag.tag
			, posttag.howManyTimesUsed

		FROM posttag
		WHERE
			posttag.id=?
	`, id)

	if err != nil {
		return result, err
	}

	for rows.Next() {
		var tag string
		var howManyTimesUsed int

		rows.Scan(&howManyTimesUsed)

		result = tags.Tag{
			Id:               id,
			Tag:              tag,
			HowManyTimesUsed: howManyTimesUsed,
			PostsLink:        CreateLinkToPostsByTag(tag),
		}
	}

	rows.Close()
	return result, nil
}

/*
Queries the database for all tags, ordered by how many times
they are used.
*/
func GetTags() (tags.TagCollection, error) {
	var err error
	result := tags.NewTagCollection()

	rows, err := database.Db.Query(`
		SELECT
			  posttag.id
			, posttag.tag
			, posttag.howManyTimesUsed

		FROM posttag
		WHERE
			posttag.howManyTimesUsed > 0
		ORDER BY
			posttag.howManyTimesUsed DESC
	`)

	if err != nil {
		return result, err
	}

	defer rows.Close()

	for rows.Next() {
		var id int
		var tag string
		var howManyTimesUsed int

		rows.Scan(&id, &tag, &howManyTimesUsed)

		newTag := tags.Tag{
			Id:               id,
			Tag:              tag,
			HowManyTimesUsed: howManyTimesUsed,
			PostsLink:        CreateLinkToPostsByTag(tag),
		}

		result.Tags = append(result.Tags, newTag)
	}

	return result, nil
}