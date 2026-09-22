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
        queryKey: ["queries", collectionId, "detail", queryId],
        queryFn: () => fetchQuery(collectionId!, queryId!),
        enabled: Boolean(collectionId && queryId),
        staleTime: 60_000,
        refetchOnWindowFocus: false,
        retry: 1,
    });

    const deleteMutation = useMutation({
        mutationFn: ({ queryId: targetId }: { queryId: string }) =>
            deleteQuery(collectionId!, targetId),
        onSuccess: () => {
            queryClient.removeQueries({
                queryKey: ["queries", collectionId, "detail", queryId],
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
