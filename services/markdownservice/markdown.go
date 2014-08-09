package markdownservice

import (
	"github.com/russross/blackfriday"
)

func ParseMarkdown(input string) []byte {
	return blackfriday.MarkdownCommon([]byte(input))
}
