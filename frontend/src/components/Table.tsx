import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import { CommentElement } from "@/types/comments";

interface Props {
  comments: CommentElement[];
}

export function CommentTable({ comments }: Props) {
  return (
    <Table>
      <TableCaption>Reddit Profile Comments</TableCaption>
      <TableHeader>
        <TableRow>
          <TableHead className="w-[120px]">Subreddit</TableHead>
          <TableHead className="w-[114px]">Date</TableHead>
          <TableHead>Comment</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {comments.map((comment_element, index) => (
          <TableRow key={index}>
            <TableCell className="font-medium">
              {comment_element.subreddit}
            </TableCell>
            <TableCell>{comment_element.date}</TableCell>
            <TableCell>{comment_element.comment}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
