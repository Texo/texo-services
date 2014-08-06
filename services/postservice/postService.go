package postservice

import (
	"fmt"
	"log"

	"github.com/texo/texo-services/database"
	"github.com/texo/texo-services/model/posts"
)

/*
Calculate start and end records based on a specified page number.
The calculation depends on knowing how many posts are displayed
per page.
*/
func CalculatePageStartEnd(page int, postsPerPage int) (int, int) {
	start := (page - 1) * postsPerPage
	end := start + postsPerPage

	return start, end
}

/*
Get Published posts.
*/
func GetPublishedPosts(page int, postsPerPage int) (posts.PostCollection, error) {
	start, end := CalculatePageStartEnd(page, postsPerPage)
	return getPosts(start, end, "Published")
}


/*
This private function retrieves posts filtered by a set of criteria.
*/
func getPosts(start int, end int, status string) (posts.PostCollection, error) {
	var err error
	var postCount int

	result := posts.NewPostCollection()

	whereClause := "1=1 "
	whereParams := make([]interface{}, 0)

	if status != "" {
		whereClause = whereClause + " AND poststatus.status=?"
		whereParams = append(whereParams, status)
	}

	countSql := fmt.Sprintf(`
		SELECT
			COUNT(post.id) AS postCount
		FROM post
			INNER JOIN poststatus ON poststatus.id=post.postStatusId
		WHERE %s
	`, whereClause)

	dataSql := fmt.Sprintf(`
		SELECT
			  post.id
			, post.title
			, post.authorId
			, CONCAT(user.firstName, ' ', user.lastName) AS author
			, post.slug
			, post.content
			, post.createdDateTime
			, post.publishedDateTime
			, post.publishedYear
			, post.publishedMonth
			, post.postStatusId
			, poststatus.status AS status
			, (
				SELECT GROUP_CONCAT(posttag.tag SEPARATOR ',')
				FROM post_posttag
					INNER JOIN posttag ON posttag.id=post_posttag.postTagId
				WHERE
					post_posttag.postId=post.id
			) AS tagList
			, (
				SELECT GROUP_CONCAT(posttag.id SEPARATOR ',')
				FROM post_posttag
					INNER JOIN posttag ON posttag.id=post_posttag.postTagId
				WHERE
					post_posttag.postId=post.id
			) AS tagIdList

		FROM post
			INNER JOIN user ON user.id=post.authorId
			INNER JOIN poststatus ON poststatus.id=post.postStatusId

		WHERE %s
		ORDER BY
			post.createdDateTime DESC
		LIMIT %d, %d
	`,
		whereClause,
		start,
		end,
	)

	/*
	 * Get a count of posts by the specified criteria.
	 */
	rows1, err := database.Db.Query(countSql, whereParams...)
	if err != nil {
		return result, err
	}

	rows1.Next()
	rows1.Scan(&postCount)
	rows1.Close()

	log.Print("Count of posts:", postCount)

	/*
	 * Get the actual post data
	 */
	rows2, err := database.Db.Query(dataSql, whereParams...)
	if err != nil {
		return result, err
	}

	defer rows2.Close()

	for rows2.Next() {
		var id                int
		var title             string
		var authorId          int
		var author            string
		var slug              string
		var content           string
		var createdDateTime   string
		var publishedDateTime string
		var publishedYear     int
		var publishedMonth    int
		var postStatusId      int
		var status            string
		var tagList           string
		var tagIdList         string

		rows2.Scan(
			&id,
			&title,
			&authorId,
			&author,
			&slug,
			&content,
			&createdDateTime,
			&publishedDateTime,
			&publishedYear,
			&publishedMonth,
			&postStatusId,
			&status,
			&tagList,
			&tagIdList,
		)

		post := posts.Post{
			Id: id,
			Title: title,
			AuthorId: authorId,
			Author: author,
			Slug: slug,
			Content: content,
			CreatedDateTime: createdDateTime,
			PublishedDateTime: publishedDateTime,
			PublishedYear: publishedYear,
			PublishedMonth: publishedMonth,
			PostStatusId: postStatusId,
			Status: status,
			TagList: tagList,
			TagIdList: tagIdList,
		}

		result.Posts = append(result.Posts, post)
	}

	return result, nil
}