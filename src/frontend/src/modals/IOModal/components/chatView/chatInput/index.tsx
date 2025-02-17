import { usePostUploadFile } from "@/controllers/API/queries/files/use-post-upload-file";
import useAlertStore from "@/stores/alertStore";
import { useRef, useState } from "react";
import ShortUniqueId from "short-unique-id";
import {
  ALLOWED_IMAGE_INPUT_EXTENSIONS,
  CHAT_INPUT_PLACEHOLDER,
  CHAT_INPUT_PLACEHOLDER_SEND,
  FS_ERROR_TEXT,
  SN_ERROR_TEXT,
} from "../../../../../constants/constants";
import { uploadFile } from "../../../../../controllers/API";
import useFlowsManagerStore from "../../../../../stores/flowsManagerStore";
import {
  ChatInputType,
  FilePreviewType,
} from "../../../../../types/components";
import FilePreview from "../filePreviewChat";
import ButtonSendWrapper from "./components/buttonSendWrapper";
import TextAreaWrapper from "./components/textAreaWrapper";
import UploadFileButton from "./components/uploadFileButton";
import { getClassNamesFilePreview } from "./helpers/get-class-file-preview";
import useAutoResizeTextArea from "./hooks/use-auto-resize-text-area";
import useFocusOnUnlock from "./hooks/use-focus-unlock";
export default function ChatInput({
  lockChat,
  chatValue,
  sendMessage,
  setChatValue,
  inputRef,
  noInput,
  files,
  setFiles,
  isDragging,
}: ChatInputType): JSX.Element {
  const [repeat, setRepeat] = useState(1);
  const saveLoading = useFlowsManagerStore((state) => state.saveLoading);
  const currentFlowId = useFlowsManagerStore((state) => state.currentFlowId);
  const [inputFocus, setInputFocus] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const setErrorData = useAlertStore((state) => state.setErrorData);
  const [id, setId] = useState<string>("");

  useFocusOnUnlock(lockChat, inputRef);
  useAutoResizeTextArea(chatValue, inputRef);

  const handleFileChange = async (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const fileInput = event.target;
    const file = fileInput.files?.[0];
    if (file) {
      const fileExtension = file.name.split(".").pop()?.toLowerCase();

      if (
        !fileExtension ||
        !ALLOWED_IMAGE_INPUT_EXTENSIONS.includes(fileExtension)
      ) {
        setErrorData({
          title: "Error uploading file",
          list: [FS_ERROR_TEXT, SN_ERROR_TEXT],
        });
        return;
      }

      const uid = new ShortUniqueId();
      const id = uid.randomUUID(10);
      setId(id);

      const type = file.type.split("/")[0];
      const blob = file;

      setFiles((prevFiles) => [
        ...prevFiles,
        { file: blob, loading: true, error: false, id, type },
      ]);

      mutation.mutate(
        { file: blob, id: currentFlowId },
        {
          onSuccess: (data) => {
            setFiles((prev) => {
              const newFiles = [...prev];
              const updatedIndex = newFiles.findIndex((file) => file.id === id);
              newFiles[updatedIndex].loading = false;
              newFiles[updatedIndex].path = data.file_path;
              return newFiles;
            });
          },
          onError: () => {
            setFiles((prev) => {
              const newFiles = [...prev];
              const updatedIndex = newFiles.findIndex((file) => file.id === id);
              newFiles[updatedIndex].loading = false;
              newFiles[updatedIndex].error = true;
              return newFiles;
            });
          },
        },
      );
    }

    fileInput.value = "";
  };

  const mutation = usePostUploadFile();

  const send = () => {
    sendMessage({
      repeat,
      files: files.map((file) => file.path ?? "").filter((file) => file !== ""),
    });
    setFiles([]);
  };

  const checkSendingOk = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    return (
      event.key === "Enter" &&
      !lockChat &&
      !saveLoading &&
      !event.shiftKey &&
      !event.nativeEvent.isComposing
    );
  };

  const classNameFilePreview = getClassNamesFilePreview(inputFocus);

  const handleButtonClick = () => {
    fileInputRef.current!.click();
  };

  return (
    <div className="flex w-full flex-col-reverse">
      <div className="relative w-full">
        <TextAreaWrapper
          checkSendingOk={checkSendingOk}
          send={send}
          lockChat={lockChat}
          noInput={noInput}
          saveLoading={saveLoading}
          chatValue={chatValue}
          setChatValue={setChatValue}
          CHAT_INPUT_PLACEHOLDER={CHAT_INPUT_PLACEHOLDER}
          CHAT_INPUT_PLACEHOLDER_SEND={CHAT_INPUT_PLACEHOLDER_SEND}
          inputRef={inputRef}
          setInputFocus={setInputFocus}
          files={files}
          isDragging={isDragging}
        />
        <div className="form-modal-send-icon-position">
          <ButtonSendWrapper
            send={send}
            lockChat={lockChat}
            noInput={noInput}
            saveLoading={saveLoading}
            chatValue={chatValue}
            files={files}
          />
        </div>

        <div
          className={`absolute bottom-2 left-4 ${
            lockChat || saveLoading ? "cursor-not-allowed" : ""
          }`}
        >
          <UploadFileButton
            lockChat={lockChat || saveLoading}
            fileInputRef={fileInputRef}
            handleFileChange={handleFileChange}
            handleButtonClick={handleButtonClick}
          />
        </div>
      </div>
      {files.length > 0 && (
        <div className={classNameFilePreview}>
          {files.map((file) => (
            <FilePreview
              error={file.error}
              file={file.file}
              loading={file.loading}
              key={file.id}
              onDelete={() => {
                setFiles((prev: FilePreviewType[]) =>
                  prev.filter((f) => f.id !== file.id),
                );
                // TODO: delete file on backend
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}
