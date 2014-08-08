package tags

type Tag struct {
	Id               int    `json:"id"`
	Tag              string `json:"tag"`
	HowManyTimesUsed int    `json:"howManyTimesUsed"`
	PostsLink        string `json:"postsLink"`
}
