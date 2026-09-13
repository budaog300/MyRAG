import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
    deleteQuery,
    fetchQueries,
    deleteQueries
} from "@/api/queries";

export const useQueries = ({
    collectionId,
    page,
    size,
}: {
    collectionId: string;
    page: number;
    size: number;
}) => {
    const queryClient = useQueryClient();

    const query = useQuery({
        queryKey: ["queries", collectionId, page, size],
        queryFn: () => fetchQueries(collectionId, { page, size }),
        enabled: Boolean(collectionId),
    });

    const deleteMutation = useMutation({
        mutationFn: ({ queryId }: { queryId: string }) =>
            deleteQuery(collectionId, queryId),
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: ["queries", collectionId],
            });
        },
    });

    const clearMutation = useMutation({
        mutationFn: () => deleteQueries(collectionId),
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: ["queries", collectionId],
            });
        },
    });

    return {
        query,
        deleteMutation,
        clearMutation
    };
};