import { Route, Routes } from "react-router-dom";
import Layout from "@/components/layout/Layout";
import CollectionsPage from "@/pages/CollectionsPage";
import CollectionPage from "@/pages/CollectionPage";
import DocumentsPage from "@/pages/DocumentsPage";
import DocumentPage from "@/pages/DocumentPage";
import NotFound from "@/components/common/NotFound";
import CollectionChat from "@/components/search/CollectionChat";

const Router = () => (
  <Routes>
    <Route path="/" element={<Layout />}>
      <Route index element={<CollectionsPage />} />
      <Route path="collections" element={<CollectionsPage />} />
      <Route path="collections/:collectionId" element={<CollectionPage />}>
        <Route index element={<CollectionChat />} />
        <Route path="documents" element={<DocumentsPage />} />
        <Route path="documents/:documentId" element={<DocumentPage />} />
      </Route>
      <Route path="*" element={<NotFound />} />
    </Route>
  </Routes>
);

export default Router;
