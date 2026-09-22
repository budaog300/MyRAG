import { lazy, Suspense } from "react";
import { Route, Routes } from "react-router-dom";
import Layout from "@/components/layout/Layout";
import Spinner from "@/components/ui/Spinner";

const CollectionsPage = lazy(() => import("@/pages/CollectionsPage"));
const CollectionPage = lazy(() => import("@/pages/CollectionPage"));
const DocumentsPage = lazy(() => import("@/pages/DocumentsPage"));
const DocumentPage = lazy(() => import("@/pages/DocumentPage"));
const NotFound = lazy(() => import("@/components/common/NotFound"));
const CollectionChat = lazy(() => import("@/components/search/CollectionChat"));
const QueriesPage = lazy(() => import("@/pages/QueriesPage"));
const QueryHistoryPage = lazy(() => import("@/pages/QueryHistoryPage"));

const PageFallback = (
  <div className="flex min-h-[40vh] items-center justify-center">
    <Spinner />
  </div>
);

const Router = () => (
  <Routes>
    <Route path="/" element={<Layout />}>
      <Route
        index
        element={
          <Suspense fallback={PageFallback}>
            <CollectionsPage />
          </Suspense>
        }
      />
      <Route
        path="collections"
        element={
          <Suspense fallback={PageFallback}>
            <CollectionsPage />
          </Suspense>
        }
      />

      <Route
        path="collections/:collectionId"
        element={
          <Suspense fallback={PageFallback}>
            <CollectionPage />
          </Suspense>
        }
      >
        <Route
          index
          element={
            <Suspense fallback={PageFallback}>
              <CollectionChat />
            </Suspense>
          }
        />

        <Route
          path="documents"
          element={
            <Suspense fallback={PageFallback}>
              <DocumentsPage />
            </Suspense>
          }
        />
        <Route
          path="documents/:documentId"
          element={
            <Suspense fallback={PageFallback}>
              <DocumentPage />
            </Suspense>
          }
        />

        <Route
          path="queries"
          element={
            <Suspense fallback={PageFallback}>
              <QueriesPage />
            </Suspense>
          }
        />
        <Route
          path="queries/:queryId"
          element={
            <Suspense fallback={PageFallback}>
              <QueryHistoryPage />
            </Suspense>
          }
        />
      </Route>

      <Route
        path="*"
        element={
          <Suspense fallback={PageFallback}>
            <NotFound />
          </Suspense>
        }
      />
    </Route>
  </Routes>
);

export default Router;
