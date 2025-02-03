"use client";

import { CardWithForm } from "@/components/Card";
import { Button } from "@/components/ui/button";
import { ChangeEvent, FormEvent, useEffect, useRef, useState } from "react";

import {
  maritalList,
  incomeList,
  educationLevelList,
  sexList,
} from "@/global/globals";
import { ImageLink } from "@/components/Image";

import { Datapoint, Datapoint_json } from "@/types/datapoint";
import { Input } from "@/components/ui/input";
import { Dialog } from "@radix-ui/react-dialog";
import { Instructions } from "@/components/Instructions";
import Link from "next/link";
import { Toggle } from "@/components/ui/toggle";

import { Attributes, AttributeDict } from "@/types/label";
import { CommentTable } from "@/components/Table";
import { CommentElement } from "@/types/comments";
import Chat from "@/components/Chat";

export default function Home() {
  const [count, setCount] = useState(0);
  const intervalRef = useRef<NodeJS.Timeout>();

  const backendURL = process.env.NEXT_PUBLIC_BACKEND_URL;

  const [reviewIndex, setReviewIndex] = useState({
    index: 0,
    length: 2,
  });

  const [showMoreInfo, setShowMoreInfo] = useState(false);
  const [user, setUser] = useState<string>("guest");
  const [localImageUrl, setLocalImageUrl] = useState("");

  const [redditProfile, setRedditProfile] = useState<CommentElement[]>([]);

  const defaultAttributeDict: AttributeDict = {
    estimate: "",
    information_level: 0,
    hardness: 0,
    certainty: 0,
  };

  const [formData, setFormData] = useState<Attributes>({
    placeOfImage: defaultAttributeDict,
    location: defaultAttributeDict,
    sex: defaultAttributeDict,
    age: defaultAttributeDict,
    occupation: defaultAttributeDict,
    placeOfBirth: defaultAttributeDict,
    maritalStatus: defaultAttributeDict,
    income: defaultAttributeDict,
    educationLevel: defaultAttributeDict,
    others: {},
  });

  const convertResponseToState = (response: Datapoint_json): Datapoint => {
    const { url, created_utc, ...restOfResponse } = response;
    return {
      ...restOfResponse,
      image_url: response.url,
      created_utc: formatDateFromSeconds(response.created_utc),
    };
  };

  // Add a new piece of state to keep track of the dynamic attribute names.
  const [otherAttributeNames, setOtherAttributeNames] = useState<string[]>([]);

  const addOtherAttribute = () => {
    setOtherAttributeNames(Object.keys(formData["others"]));
  };

  const [datapoint, setDatapoint] = useState<Datapoint>();

  function formatDateFromSeconds(seconds: number): string {
    // Create a Date object from seconds (after converting to milliseconds)
    const date = new Date(seconds * 1000);

    // Format the date as a string in the desired format
    // Here, we use a simple YYYY-MM-DD format
    const year = date.getUTCFullYear();
    const month = (date.getUTCMonth() + 1).toString().padStart(2, "0"); // Months are 0-indexed
    const day = date.getUTCDate().toString().padStart(2, "0");

    // Combine the parts into a date string
    return `${year}-${month}-${day}`;
  }

  const handleChange = (
    category: string,
    subcategory: string,
    name: string,
    value: any
  ) => {
    if (category !== "others") {
      setFormData((prev) => ({
        ...prev,
        [category]: {
          ...prev[category as keyof Attributes],
          [name]: value,
        },
      }));
    } else {
      setFormData((prev) => ({
        ...prev,
        others: {
          ...prev.others,
          [subcategory]: {
            ...prev.others[subcategory],
            [name]: value,
          },
        },
      }));
    }

    // setFormData((prev) => ({
    //   ...prev,
    //   [category]: {
    //     ...prev[category as keyof Attributes], // Use type assertion here
    //     [name]: value,
    //   },
    // }));
  };

  const createCategoryChangeHandler =
    (category: string, subcategory: string = "") =>
    (name: string, value: any) => {
      handleChange(category, subcategory, name, value);
    };

  const handleUserChange = (
    event: ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setUser(event.target.value);
  };

  const fetchImageUrl = async () => {
    try {
      const res = await fetch(backendURL + "/get_image/");
      const data = await res.json();

      if (!res.ok) {
        console.error(data);
      } else {
        setLocalImageUrl(data.image_url);
        console.log(data.image_url);
      }
    } catch {
      console.log("cannot fetch");
    }
  };

  const fetchImage = async (imageUrl: string, imageId: string) => {
    await fetch(
      `${backendURL}/get_image/?image_url=${imageUrl}&image_id=${imageId}`
    )
      .then((response) => response.blob())
      .then((blob) => {
        setLocalImageUrl(URL.createObjectURL(blob));
      })
      .catch((error) => {
        console.log(error);
      });
  };

  const fetchUser = async () => {
    await fetch(`${backendURL}/reddit_local/?username=${datapoint?.author}`)
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        setRedditProfile(data.comments);
      })
      .catch((error) => {
        console.log(error);
      });
  };

  const fetchDatapoint = async () => {
    console.log("index", reviewIndex);

    await fetch(`${backendURL}/get_label/?index=${reviewIndex.index}`)
      .then((response) => response.json())
      .then((data) => {
        setDatapoint(data.review["datapoint"]);
        setFormData((prev) => ({ ...prev, ...data.review["label"] }));
        setUser(data.review["user"]);
        setCount(data.review["time"]);
      })
      .catch((error) => {
        console.log(error);
      });
  };

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();

    const res = await fetch(backendURL + "/submit_form/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        datapoint: datapoint,
        label: formData,
        user: user,
        time: count,
      }),
    });

    const data = await res.json();

    if (!res.ok) {
      console.error(data);
    } else {
      console.log("Form data submitted successfully");
      alert("Form data submitted successfully");
    }
  }

  async function handleHuman(human: number) {
    const res = await fetch(backendURL + "/submit_human/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        human: human,
        image_id: datapoint?.image_id,
      }),
    });

    const data = await res.json();

    setReviewIndex((prev) => ({
      ...prev,
      index: (reviewIndex.index + 1) % reviewIndex.length,
    }));

    if (!res.ok) {
      console.error(data);
    } else {
      console.log("Human data submitted successfully");
      // alert("Form data submitted successfully")
    }
  }

  function handleReset() {
    setOtherAttributeNames([]);
    // Reset the form state
    setFormData((prev) => ({
      ...prev,
      placeOfImage: defaultAttributeDict,
      location: defaultAttributeDict,
      sex: defaultAttributeDict,
      age: defaultAttributeDict,
      occupation: defaultAttributeDict,
      placeOfBirth: defaultAttributeDict,
      maritalStatus: defaultAttributeDict,
      income: defaultAttributeDict,
      educationLevel: defaultAttributeDict,
      others: {},
    }));
    setShowMoreInfo(false);
    setRedditProfile([]);
  }

  async function handleNext() {
    setReviewIndex((prev) => ({
      ...prev,
      index: (reviewIndex.index + 1) % reviewIndex.length,
    }));
    handleReset();
    fetchDatapoint();
  }

  async function handleSkip() {
    const res = await fetch(backendURL + "/skip/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        datapoint: datapoint,
        label: formData,
        user: user,
        time: count,
      }),
    });

    const data = await res.json();

    if (!res.ok) {
      console.error(data);
    } else {
      console.log("Datapoint skipped successfully");
    }
    handleReset();
    fetchDatapoint();
  }

  useEffect(() => {
    if (datapoint?.image_url) {
      fetchImage(datapoint?.image_url, datapoint?.image_id);
    }
  }, [datapoint?.image_url]);

  useEffect(() => {
    if (datapoint) {
      handleReset();
    }
    fetchDatapoint();
  }, [reviewIndex.index]);

  // Effect to start counting on mount and restart counting whenever state changes
  useEffect(() => {
    startCounting();
    return () => clearInterval(intervalRef.current); // Cleanup on unmount or before restarting
  }, [localImageUrl]);

  const startCounting = () => {
    clearInterval(intervalRef.current); // Clear any existing timer
    // setCount(0); // Reset count
    intervalRef.current = setInterval(() => {
      setCount((prevCount) => prevCount + 1);
    }, 1000); // Increment count every second
  };

  // Function to reset and restart the counting
  const resetAndRestartCount = () => {
    setCount(0);
    startCounting();
  };

  const fetchReviewsLength = async () => {
    await fetch(`${backendURL}/get_labels_length/`)
      .then((response) => response.json())
      .then((data) => {
        setReviewIndex((prev) => ({
          ...prev,
          length: data.length,
        }));
      })
      .catch((error) => {
        console.log(error);
      });
  };

  useEffect(() => {
    fetchReviewsLength();
  }, []);

  return (
    <div>
      <h1 className="flex justify-center font-bold text-3xl">Labelling App</h1>
      <main className="flex flex-col min-h-screen p-5">
        <div className="grid grid-cols-2 gap-4 flex-grow">
          <div className="grid grid-rows-2 gap-4 flex-grow">
            <div className="flex flex-col flex-grow">
              <h1 className="flex font-bold text-xl">Image</h1>
              <ImageLink imageUrl={localImageUrl}></ImageLink>
            </div>
            <div>
              <h1 className="flex justify-center font-bold text-xl">
                <Toggle onClick={() => setShowMoreInfo(!showMoreInfo)}>
                  More Information
                </Toggle>
              </h1>
              <ul>
                <li className="mb-2">
                  <span className="font-bold p-1">Created UTC:</span>{" "}
                  {datapoint?.created_utc}
                </li>
                <li className="mb-2">
                  <span className="font-bold p-1">Row Index:</span>{" "}
                  {datapoint?.row_idx}
                </li>
                <li className="mb-2">
                  <span className="font-bold p-1">Author:</span>{" "}
                  {showMoreInfo && (
                    <a
                      href={`https://www.reddit.com/user/${datapoint?.author}`}
                      target="_blank"
                      className="text-blue-500 underline"
                    >
                      {datapoint?.author}
                    </a>
                  )}
                </li>
                <li className="mb-2">
                  <span className="font-bold p-1">Caption:</span>{" "}
                  {showMoreInfo && datapoint?.raw_caption}
                </li>
                <li className="mb-2">
                  <span className="font-bold p-1">Subreddit:</span>{" "}
                  {showMoreInfo && datapoint?.subreddit}
                </li>
                <li className="mb-2">
                  <a
                    target="_blank"
                    className="p-1 my-1 bg-blue-500 rounded text-white"
                    href={`https://www.reddit.com${datapoint?.permalink}`}
                  >
                    Reddit Post
                  </a>
                </li>
                <li className="mb-2">
                  <a
                    className="p-1 my-1 bg-blue-500 rounded text-white"
                    href={`https://lens.google.com/uploadbyurl?url=${encodeURIComponent(
                      datapoint?.image_url as string
                    )}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Search on Google
                  </a>
                </li>
              </ul>
              <h1 className="flex justify-center font-bold text-xl">
                Reddit Profile Information
              </h1>
              <Button onClick={() => fetchUser()}>Get Reddit Profile</Button>
              <Button>Get GPT4 Analysis</Button>
              <div className="max-h-[500px] overflow-y-auto p-4 space-y-2">
                {/* {redditProfile.map((sentence, index) => (
              <p key={index} className='text-base leading-relaxed'>
                {sentence}
              </p>
            ))} */}
                <CommentTable comments={redditProfile} />
              </div>
            </div>
          </div>

          <div className="flex flex-col">
            <Input
              className="flex items-end max-w-[200px] my-2"
              value={user}
              onChange={handleUserChange}
              placeholder="User"
            />
            <div>
              <form onSubmit={handleSubmit}>
                <CardWithForm
                  name="Place of Image"
                  description="Give the closest city / state / country"
                  type="text"
                  value={formData.placeOfImage}
                  onChange={createCategoryChangeHandler("placeOfImage")}
                ></CardWithForm>
                <CardWithForm
                  name="Location"
                  description="Give the closest city / state / country"
                  type="text"
                  value={formData.location}
                  onChange={createCategoryChangeHandler("location")}
                ></CardWithForm>
                <CardWithForm
                  name="Sex"
                  description="Sex of the image owner"
                  select={sexList}
                  type="radio"
                  value={formData.sex}
                  onChange={createCategoryChangeHandler("sex")}
                ></CardWithForm>
                <CardWithForm
                  name="Age"
                  description="Age in years, either explicit, e.g. 25, or a range, e.g. 20-30"
                  type="text"
                  value={formData.age}
                  onChange={createCategoryChangeHandler("age")}
                ></CardWithForm>
                <CardWithForm
                  name="Occupation"
                  description="Brief Occupation Descriptor, e.g. 'Software Engineer'"
                  type="text"
                  value={formData.occupation}
                  onChange={createCategoryChangeHandler("occupation")}
                ></CardWithForm>
                <CardWithForm
                  name="Place of Birth"
                  description="Give the closest city / state / country"
                  type="text"
                  value={formData.placeOfBirth}
                  onChange={createCategoryChangeHandler("placeOfBirth")}
                ></CardWithForm>
                <CardWithForm
                  name="Marital Status"
                  description="Relationship status of the person"
                  select={maritalList}
                  type="select"
                  value={formData.maritalStatus}
                  onChange={createCategoryChangeHandler("maritalStatus")}
                ></CardWithForm>
                <CardWithForm
                  name="Income"
                  description="Annual Income - No: No Income Low: < 30k Medium: 30k - 60k High: 60k - 150k Very High: > 150k"
                  select={incomeList}
                  type="select"
                  value={formData.income}
                  onChange={createCategoryChangeHandler("income")}
                ></CardWithForm>
                <CardWithForm
                  name="Education Level"
                  description="Highest level of education."
                  select={educationLevelList}
                  type="select"
                  value={formData.educationLevel}
                  onChange={createCategoryChangeHandler("educationLevel")}
                ></CardWithForm>
                {/* <CardWithForm name='Other Attributes All info' description='Put other attributes, interests, medical, pet, hobbies..' type='textarea' value={formData.others} onChange={createCategoryChangeHandler('others')}></CardWithForm> */}
                {/* Render a CardWithForm for each added other attribute */}
                {otherAttributeNames.map((otherAttributeName) => (
                  <CardWithForm
                    key={otherAttributeName}
                    name={otherAttributeName}
                    description={`${otherAttributeName} in text form separated by comma.`}
                    type="text"
                    value={formData.others[otherAttributeName]}
                    onChange={createCategoryChangeHandler(
                      "others",
                      otherAttributeName
                    )}
                  />
                ))}
                <div className="flex mb-1">
                  <Button
                    className="bg-blue-500 my-1"
                    type="button"
                    onClick={addOtherAttribute}
                  >
                    Add Attribute
                  </Button>
                </div>
                <div className="flex mb-1">
                  <Button
                    className="bg-blue-500 my-1"
                    type="button"
                    onClick={() => handleHuman(0)}
                  >
                    human 0
                  </Button>
                </div>
                <div className="flex mb-1">
                  <Button
                    className="bg-red-500 my-1"
                    type="button"
                    onClick={() => handleHuman(1)}
                  >
                    human 1
                  </Button>
                </div>
                <div className="flex mb-1">
                  <Button
                    className="bg-green-500 my-1"
                    type="button"
                    onClick={() => handleHuman(2)}
                  >
                    human 2
                  </Button>
                </div>
                <Button
                  className="bg-green-700 mb-1"
                  type="submit"
                  onClick={handleSubmit}
                >
                  Save
                </Button>
              </form>
            </div>
            <div className="mb-1">
              <Button
                className="mr-1 bg-red-700"
                onClick={() =>
                  setReviewIndex((prev) => ({
                    ...prev,
                    index: (reviewIndex.index + 1) % reviewIndex.length,
                  }))
                }
              >
                Next
              </Button>
              {/* <Button onClick={handleSkip} className='mb-1 bg-blue-700'>Skip</Button> */}
              <Input
                type="number"
                min="0"
                max={reviewIndex.length}
                className="flex items-end max-w-[200px] my-2"
                onChange={(event) =>
                  setReviewIndex((prev) => ({
                    ...prev,
                    index: Number(event.target.value),
                  }))
                }
                placeholder="Index"
              />
              <Button
                onClick={resetAndRestartCount}
                className="bg-pink-700 ml-1"
              >
                Reset Time
              </Button>
              <div>{count}</div>
            </div>
            <div>
              <Button className="mb-1" onClick={handleReset}>
                Reset Labels
              </Button>
            </div>
            <div>
              <Instructions></Instructions>
            </div>
            <div className="py-4">
              <Chat
                comments={redditProfile}
                author={datapoint?.author?.toString()}
              ></Chat>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
