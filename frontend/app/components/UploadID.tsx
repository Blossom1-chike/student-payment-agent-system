export default function UploadID({ onUpload }: { onUpload: (file: File) => void }) {
  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      onUpload(e.target.files[0]);
    }
  };

  return <input type="file" accept="image/*" onChange={handleFile} className="border p-2 rounded" />;
}
