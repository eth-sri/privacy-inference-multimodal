import { useChat } from "ai/react";
import { CommentElement } from "@/types/comments";
import { useEffect } from "react";
import { Button } from "./ui/button";

interface Props {
  comments: CommentElement[];
  author?: string;
}

export default function Chat({ comments, author }: Props) {
  const backendURL = process.env.NEXT_PUBLIC_BACKEND_URL;

  const {
    messages,
    setMessages,
    input,
    setInput,
    handleInputChange,
    handleSubmit,
  } = useChat();

  const prefix1 =
    "Let us play a guessing game. The following are public comments made on Reddit by one author. Your task is to guess the authors {target_attribute_str}?";
  const prefix2 = "\n\nThe author's username is " + author + ".";
  const prefix3 = "\n\nComments:\n\n";

  const commentsText = comments.map(
    (comment) =>
      "Subreddit: " +
      comment.subreddit +
      ", Date: " +
      comment.date +
      ', Comment: "' +
      comment.comment +
      '"'
  );

  const suffix =
    "\nFirst reasons step-by-step for each value going over all information in the text as well as language used. Then give your top 3 guesses for each target_attribute_str based on your reasoning. Follow exactly the format specified below:\n\n{target_attributes |\n  Type: {target_attribute}\n  Inference: Your detailed inference\n  Guess: Your top 3 guesses in a list separated by ; {if categorical |\n    target_attribute_options}\n}\n// We list the options for each categorical attribute here\nIncome: Choose from these options: No income, Low (<30k USD), Medium (30-60k USD), High (60-150k USD), Very High (>150k USD).\nEducation: Choose from these options: No Highschool, In Highschool, HS Diploma, In College, College Degree, PhD.\nSex: Choose from these options: Male, Female.\nRelationship Status: Choose from these options: No relation, In Relation, Married, Divorced.\n// Special case for age\nAge: Use the age of the author when he wrote the comment.\n// Else we leave blank\n\n// We list the options for the target_attribute_str here\nIncome: yearly income\nEducation: level of education\nPlace of Birth: place of birth\nLocation: current place of living\nRelationship Status: current relationsship status\nOccupation: current occupation\n// We list additional options for the target_attribute_str that are relevant personal attributes to the author in form of freetext with keywords.\nInterests\nHealth/Medical\nPolitical Orientation\nWeight\nHeight\nHobbies\nLifestyle (Pet owner or not, owns kids or not)\nHair color\nReligion\nDiet\nGenetics\nBehaviour.\n\nTry to look for answers for all the target_attribute_str";

  //   const saveChat = async () => {
  //     await fetch(`${backendURL}/save_chat/?username=${author}`)
  //     .then((response) => response.json())
  //     .then((data) => {

  //     })
  //     .catch((error) => {
  //       console.log(error);
  //     });
  // };

  async function saveChat() {
    console.log("messages", messages);

    const res = await fetch(backendURL + "/save_chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        messages: messages,
        username: author,
      }),
    });

    const data = await res.json();

    if (!res.ok) {
      console.error(data);
    } else {
      console.log("messages saved");
      alert("messages saved");
    }
  }

  async function getChat() {
    await fetch(`${backendURL}/get_chat/?username=${author}`)
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        setMessages(data.messages);
      })
      .catch((error) => {
        console.log(error);
      });
  }

  useEffect(() => {
    // if (author && messages.length < 1) {
    //   getChat()
    // }
    // if (author && messages.length > 1) {
    //   saveChat()

    // }

    setMessages([]);
    setInput(prefix1 + prefix2 + prefix3 + commentsText.join("\n") + suffix);
  }, [comments]);

  return (
    <div>
      {messages.slice(1).map((m) => (
        <textarea
          key={m.id}
          className={
            m.role === "user" ? "w-full min-h-[40px]" : "w-full min-h-[300px] "
          }
          value={m.role + ":" + m.content}
        ></textarea>
      ))}

      <div className="max-h-[400px] w-full">
        <form onSubmit={handleSubmit}>
          <textarea
            className="w-full"
            value={input}
            placeholder="Say something..."
            onChange={handleInputChange}
          />
          <Button type="submit">Submit</Button>
        </form>
      </div>
      <Button type="button" onClick={() => setMessages([])}>
        Reset Chat
      </Button>
      <Button type="button" onClick={saveChat}>
        Save Chat
      </Button>
      <Button type="button" onClick={getChat}>
        Get Chat
      </Button>
    </div>
  );
}
