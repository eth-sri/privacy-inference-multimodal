export interface Datapoint_json {
  row_idx: number | null;
  image_id: string;
  author: string | null;
  url: string;
  raw_caption: string;
  caption: string;
  subreddit: string;
  score: number;
  created_utc: number;
  permalink: string;
  crosspost_parents: string[] | null;
}

export interface Datapoint {
  row_idx: number | null;
  image_id: string;
  author: string | null;
  image_url: string;
  raw_caption: string;
  caption: string;
  subreddit: string;
  score: number;
  created_utc: string;
  permalink: string;
  crosspost_parents: string[] | null;
}