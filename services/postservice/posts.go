package postservice

import (
	"fmt"
	"math"

	"github.com/texo/texo-services/database"
	"github.com/texo/texo-services/model/posts"
)

/*
Calculates the number of pages available based on the number
of posts divided by the number of posts per page.
*/
func CalculateNumberOfPages(postCount int, postsPerPage int) int {
	return int(math.Ceil(float64(postCount) / float64(postsPerPage)));
}

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
Creates a permalink useful for going directly to a specific
blog post. The format is in the form of _/post/{year}/{month}/{slug}_
*/
func CreatePermalink(year, month int, slug string) string {
	return fmt.Sprintf("/post/%d/%d/%s", year, month, slug);
}

/*
Get a single post by year, month and slug.
*/
func GetPost(year, month int, slug string) (posts.Post, error) {
	post := posts.Post{}
	posts, err := getPosts(1, 1, "Published", year, month, slug, "", "")

	if len(posts.Posts) > 0 {
		post = posts.Posts[0]
	}

	return post, err
}

/*
Get Published posts.
*/
func GetPublishedPosts(page int, postsPerPage int) (posts.PostCollection, error) {
	return getPosts(page, postsPerPage, "Published", 0, 0, "", "", "")
}

/*
Get Published posts by tag.
*/
func GetPublishedPostsByTag(page int, postsPerPage int, tag string) (posts.PostCollection, error) {
	return getPosts(page, postsPerPage, "Published", 0, 0, "", tag, "")
}

/*
Get Published posts by search term.
*/
func GetPublishedPostsByTerm(page int, postsPerPage int, term string) (posts.PostCollection, error) {
	return getPosts(page, postsPerPage, "Published", 0, 0, "", "", term)
}


/*
This private function retrieves posts filtered by a set of criteria.
*/
func getPosts(page int, postsPerPage int, status string, year, month int, slug, tag, term string) (posts.PostCollection, error) {
	var err error
	var postCount int
	result := posts.NewPostCollection()

	/*
	 * Add current and previous pages
	 */
	result.CurrentPage = page
	if page > 1 {
		result.PreviousPage = page - 1
	} else {
		result.PreviousPage = 1
	}

	/*
	 * Calculate the start and end records for SQL paging
	 */
	start, end := CalculatePageStartEnd(page, postsPerPage)

	/*
	 * Build a WHERE clause to be used in both the count
	 * and data queries.
	 */
	whereClause := "1=1"
	whereParams := make([]interface{}, 0)

	if status != "" {
		whereClause = whereClause + " AND poststatus.status=?"
		whereParams = append(whereParams, status)
	}

	if year > 0 {
		whereClause = whereClause + " AND post.publishedYear=?"
		whereParams = append(whereParams, year)
	}

	if month > 0 {
		whereClause = whereClause + " AND post.publishedMonth=?"
		whereParams = append(whereParams, month)
	}

	if slug != "" {
		whereClause = whereClause + " AND post.slug=?"
		whereParams = append(whereParams, slug)
	}

	if tag != "" {
		whereClause = whereClause + `
			AND (
				SELECT COUNT(post_posttag.postId)
				FROM post_posttag
					INNER JOIN posttag ON posttag.id=post_posttag.postTagId
				WHERE
					post_posttag.postId=post.id
					AND posttag.tag=?
			) > 0
		`
		whereParams = append(whereParams, tag)
	}

	if term != "" {
		whereClause = whereClause + `
			AND (
				post.title LIKE ?
				OR post.content LIKE ?
			)
		`
		whereParams = append(whereParams, fmt.Sprintf("%%%s%%", term))
		whereParams = append(whereParams, fmt.Sprintf("%%%s%%", term))
	}

	/*
	 * Post count query
	 */
	countSql := fmt.Sprintf(`
		SELECT
			COUNT(post.id) AS postCount
		FROM post
			INNER JOIN poststatus ON poststatus.id=post.postStatusId
		WHERE %s
	`, whereClause)

	/*
	 * Post data query
	 */
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

	result.NumPosts = postCount
	result.NumPages = CalculateNumberOfPages(postCount, postsPerPage)
	result.LastPage = result.NumPages

	if page < result.NumPages {
		result.NextPage = page + 1
	} else {
		result.NextPage = page
	}

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
			Permalink: CreatePermalink(publishedYear, publishedMonth, slug),
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