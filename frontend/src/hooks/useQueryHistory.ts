import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
    deleteQuery,
    fetchQuery,
} from "@/api/queries";

export const useQueryHistory = (
    collectionId?: string,
    queryId?: string,
) => {
    const queryClient = useQueryClient();

    const query = useQuery({
        queryKey: ["query", collectionId, queryId],
        queryFn: () => fetchQuery(collectionId!, queryId!),
        enabled: Boolean(collectionId && queryId),
    });

    const deleteMutation = useMutation({
        mutationFn: ({ queryId }: { queryId: string }) =>
            deleteQuery(collectionId!, queryId),
        onSuccess: () => {
            queryClient.removeQueries({
                queryKey: ["query", collectionId, queryId],
            });
            queryClient.invalidateQueries({
                queryKey: ["queries", collectionId],
            });
        },
    });

    return {
        query,
        deleteMutation,
    };
};